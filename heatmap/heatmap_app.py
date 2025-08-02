#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, render_template, send_from_directory
from flask_cors import CORS
import mysql.connector
from db_config import get_db_config
import json
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

def get_db_connection():
    """获取数据库连接"""
    try:
        config = get_db_config()
        connection = mysql.connector.connect(**config)
        return connection
    except Exception as e:
        print(f"数据库连接错误: {e}")
        return None

def get_heatmap_data():
    """获取热力图数据：动物种类在各摄像头点位的分布"""
    try:
        connection = get_db_connection()
        if not connection:
            return []
        
        cursor = connection.cursor(dictionary=True)
        
        # 查询每个摄像头位置的动物种类分布
        query = """
        SELECT 
            sensor_id,
            location,
            longitude,
            latitude,
            object as animal_type,
            animal,
            caption,
            COUNT(*) as count,
            AVG(confidence) as avg_confidence,
            AVG(percentage) as avg_percentage,
            GROUP_CONCAT(DISTINCT image_path ORDER BY created_at DESC LIMIT 3) as sample_images,
            MAX(created_at) as last_detection
        FROM image_info 
        WHERE longitude IS NOT NULL 
        AND latitude IS NOT NULL 
        AND longitude != '' 
        AND latitude != ''
        AND object IS NOT NULL
        GROUP BY sensor_id, location, longitude, latitude, object, animal, caption
        ORDER BY sensor_id, count DESC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        # 转换数据格式
        heatmap_data = []
        for row in results:
            try:
                lat = float(row['latitude'])
                lng = float(row['longitude'])
                
                heatmap_data.append({
                    'sensor_id': row['sensor_id'],
                    'location': row['location'],
                    'latitude': lat,
                    'longitude': lng,
                    'animal_type': row['animal_type'],
                    'animal': row['animal'] or row['animal_type'],
                    'count': row['count'],
                    'avg_confidence': round(float(row['avg_confidence'] or 0), 2),
                    'avg_percentage': round(float(row['avg_percentage'] or 0), 2),
                    'sample_images': row['sample_images'],
                    'last_detection': str(row['last_detection']) if row['last_detection'] else None,
                    'intensity': row['count'],  # 热力图强度
                    'caption': row['caption'] or f"在{row['location']}发现{row['animal'] or row['animal_type']}，共检测到{row['count']}次"
                })
            except (ValueError, TypeError) as e:
                print(f"数据转换错误: {e}, 行数据: {row}")
                continue
        
        cursor.close()
        connection.close()
        
        return heatmap_data
        
    except Exception as e:
        print(f"获取热力图数据错误: {e}")
        return []

def get_sensor_locations():
    """获取所有摄像头位置信息"""
    try:
        connection = get_db_connection()
        if not connection:
            return []
        
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT DISTINCT
            sensor_id,
            location,
            longitude,
            latitude,
            COUNT(*) as total_detections
        FROM image_info 
        WHERE longitude IS NOT NULL 
        AND latitude IS NOT NULL 
        AND longitude != '' 
        AND latitude != ''
        GROUP BY sensor_id, location, longitude, latitude
        ORDER BY total_detections DESC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        sensors = []
        for row in results:
            try:
                lat = float(row['latitude'])
                lng = float(row['longitude'])
                
                sensors.append({
                    'sensor_id': row['sensor_id'],
                    'location': row['location'],
                    'latitude': lat,
                    'longitude': lng,
                    'total_detections': row['total_detections']
                })
            except (ValueError, TypeError):
                continue
        
        cursor.close()
        connection.close()
        
        return sensors
        
    except Exception as e:
        print(f"获取摄像头位置错误: {e}")
        return []

def get_animal_stats():
    """获取动物种类统计数据"""
    try:
        connection = get_db_connection()
        if not connection:
            return []
        
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT 
            COALESCE(animal, object) as animal_name,
            COUNT(*) as count,
            COUNT(DISTINCT sensor_id) as sensor_count,
            AVG(confidence) as avg_confidence
        FROM image_info 
        WHERE object IS NOT NULL
        GROUP BY COALESCE(animal, object)
        ORDER BY count DESC
        LIMIT 20
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        stats = []
        for row in results:
            stats.append({
                'animal_name': row['animal_name'],
                'count': row['count'],
                'sensor_count': row['sensor_count'],
                'avg_confidence': round(float(row['avg_confidence'] or 0), 2)
            })
        
        cursor.close()
        connection.close()
        
        return stats
        
    except Exception as e:
        print(f"获取动物统计错误: {e}")
        return []

@app.route('/')
def index():
    """主页面"""
    return send_from_directory('.', 'index.html')

@app.route('/api/heatmap-data')
def api_heatmap_data():
    """热力图数据API"""
    data = get_heatmap_data()
    return jsonify({
        'status': 'success',
        'data': data,
        'count': len(data)
    })

@app.route('/api/sensor-locations')
def api_sensor_locations():
    """摄像头位置API"""
    data = get_sensor_locations()
    return jsonify({
        'status': 'success',
        'data': data,
        'count': len(data)
    })

@app.route('/api/animal-stats')
def api_animal_stats():
    """动物统计API"""
    data = get_animal_stats()
    return jsonify({
        'status': 'success',
        'data': data,
        'count': len(data)
    })

@app.route('/api/point-details')
def api_point_details():
    """获取特定点位的详细信息"""
    from flask import request
    
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    
    if not lat or not lng:
        return jsonify({'status': 'error', 'message': '缺少坐标参数'})
    
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'status': 'error', 'message': '数据库连接失败'})
        
        cursor = connection.cursor(dictionary=True)
        
        # 查询该点位的详细信息
        query = """
        SELECT 
            sensor_id,
            location,
            longitude,
            latitude,
            object as animal_type,
            animal,
            caption,
            image_path,
            confidence,
            percentage,
            created_at,
            COUNT(*) OVER (PARTITION BY sensor_id, object) as total_count
        FROM image_info 
        WHERE ABS(latitude - %s) < 0.001 
        AND ABS(longitude - %s) < 0.001
        AND object IS NOT NULL
        ORDER BY created_at DESC
        LIMIT 10
        """
        
        cursor.execute(query, (float(lat), float(lng)))
        results = cursor.fetchall()
        
        if not results:
            return jsonify({'status': 'error', 'message': '未找到该点位的数据'})
        
        # 处理数据
        point_info = {
            'sensor_id': results[0]['sensor_id'],
            'location': results[0]['location'],
            'latitude': float(lat),
            'longitude': float(lng),
            'detections': []
        }
        
        for row in results:
            point_info['detections'].append({
                'animal_type': row['animal_type'],
                'animal': row['animal'] or row['animal_type'],
                'caption': row['caption'],
                'image_path': row['image_path'],
                'confidence': round(float(row['confidence'] or 0), 2),
                'percentage': round(float(row['percentage'] or 0), 2),
                'created_at': str(row['created_at']),
                'total_count': row['total_count']
            })
        
        # 使用第一条记录的caption作为点位的主要描述，如果没有则生成
        if results[0]['caption']:
            point_info['caption'] = results[0]['caption']
        else:
            animals = {}
            for detection in point_info['detections']:
                animal = detection['animal']
                if animal not in animals:
                    animals[animal] = 0
                animals[animal] += 1
            
            animal_summary = ', '.join([f"{animal}({count}次)" for animal, count in animals.items()])
            point_info['caption'] = f"摄像头{point_info['sensor_id']}位于{point_info['location']}，检测到：{animal_summary}"
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'status': 'success',
            'data': point_info
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/heatmap-by-animal/<animal_name>')
def api_heatmap_by_animal(animal_name):
    """按动物种类筛选的热力图数据"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'status': 'error', 'message': '数据库连接失败'})
        
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT 
            sensor_id,
            location,
            longitude,
            latitude,
            COUNT(*) as count,
            AVG(confidence) as avg_confidence
        FROM image_info 
        WHERE (animal = %s OR object = %s)
        AND longitude IS NOT NULL 
        AND latitude IS NOT NULL 
        AND longitude != '' 
        AND latitude != ''
        GROUP BY sensor_id, location, longitude, latitude
        ORDER BY count DESC
        """
        
        cursor.execute(query, (animal_name, animal_name))
        results = cursor.fetchall()
        
        data = []
        for row in results:
            try:
                lat = float(row['latitude'])
                lng = float(row['longitude'])
                
                data.append({
                    'sensor_id': row['sensor_id'],
                    'location': row['location'],
                    'latitude': lat,
                    'longitude': lng,
                    'count': row['count'],
                    'avg_confidence': round(float(row['avg_confidence'] or 0), 2),
                    'intensity': row['count']
                })
            except (ValueError, TypeError):
                continue
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'status': 'success',
            'data': data,
            'animal': animal_name,
            'count': len(data)
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    # 确保heatmap目录存在
    if not os.path.exists('heatmap'):
        os.makedirs('heatmap')
    
    print("🗺️ 动物分布热力图系统启动中...")
    print("📍 访问地址: http://127.0.0.1:5003")
    print("🔥 热力图数据API: http://127.0.0.1:5003/api/heatmap-data")
    print("📊 动物统计API: http://127.0.0.1:5003/api/animal-stats")
    
    app.run(host='0.0.0.0', port=5004, debug=True)
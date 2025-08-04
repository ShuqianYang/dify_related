# app.py
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import os
from get_map_data import get_map_data, get_location_detail
from get_animal_list import get_animal_list

app = Flask(__name__)
CORS(app)

# 静态文件路由
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/styles.css')
def styles():
    return send_from_directory('.', 'styles.css')

@app.route('/script.js')
def script():
    return send_from_directory('.', 'script.js')

# API路由
@app.route('/api/map-data')
def api_map_data():
    """获取地图数据API"""
    try:
        animal_type = request.args.get('animal_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        data = get_map_data(animal_type, start_date, end_date)
        return jsonify(data)
    except Exception as e:
        print(f"API错误: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/animal-list')
def api_animal_list():
    """获取动物列表API"""
    try:
        animals = get_animal_list()
        return jsonify(animals)
    except Exception as e:
        print(f"API错误: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/location-detail')
def api_location_detail():
    """获取地点详情API"""
    longitude = request.args.get('longitude', type=float)
    latitude = request.args.get('latitude', type=float)
    location = request.args.get('location')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    print(f"🔍 API调用参数: longitude={longitude}, latitude={latitude}, location={location}, start_date={start_date}, end_date={end_date}")
    
    try:
        details = get_location_detail(
            longitude=longitude,
            latitude=latitude,
            location=location,
            start_date=start_date,
            end_date=end_date
        )
        print(f"📊 API返回数据: {details}")
        return jsonify(details)
    except Exception as e:
        print(f"❌ API错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 启动动物分布地图可视化系统...")
    print("📍 访问地址: http://localhost:5005")
    app.run(debug=True, host='0.0.0.0', port=5005)
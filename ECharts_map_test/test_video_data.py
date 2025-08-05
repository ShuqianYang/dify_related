#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试视频数据插入脚本
用于测试视频和图片混合显示功能
"""

import mysql.connector
from datetime import datetime
import sys
sys.path.append('ECharts_map')  # 运行系统路径改为'ECharts_map'
from db_config import get_db_config, get_table_name

# 获取数据库配置
DB_CONFIG = get_db_config()
TABLE_NAME = get_table_name()

def insert_test_video_data():
    """插入测试视频数据"""
    try:
        # 连接数据库
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # 测试视频数据
        test_videos = [
            {
                'object': '野生动物监测',
                'animal': '东北虎',
                'longitude': 'E124.5',
                'latitude': 'N47.8',
                'location': '大兴安岭',
                'path': 'https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4',
                'type': 'video',
                'caption': '东北虎在雪地中觅食的珍贵视频记录',
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'object': '野生动物监测',
                'animal': '大熊猫',
                'longitude': 'E103.1',
                'latitude': 'N31.02',
                'location': '成都',
                'path': 'https://sample-videos.com/zip/10/mp4/SampleVideo_640x360_1mb.mp4',
                'type': 'video',
                'caption': '大熊猫在竹林中嬉戏的视频片段',
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'object': '野生动物监测',
                'animal': '金丝猴',
                'longitude': 'E119.0',
                'latitude': 'N30.3',
                'location': '芜湖',
                'path': 'https://sample-videos.com/zip/10/mp4/SampleVideo_720x480_1mb.mp4',
                'type': 'video',
                'caption': '金丝猴群体活动的监测视频',
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        ]
        
        # 插入数据的SQL语句
        insert_sql = f"""
        INSERT INTO {TABLE_NAME} 
        (object, animal, longitude, latitude, location, path, type, caption, time)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        print("🎬 开始插入测试视频数据...")
        
        for i, video_data in enumerate(test_videos, 1):
            cursor.execute(insert_sql, (
                video_data['object'],
                video_data['animal'],
                video_data['longitude'],
                video_data['latitude'],
                video_data['location'],
                video_data['path'],
                video_data['type'],
                video_data['caption'],
                video_data['time']
            ))
            print(f"   ✅ 插入视频 {i}: {video_data['animal']} - {video_data['location']}")
        
        # 提交事务
        connection.commit()
        print(f"\n🎉 成功插入 {len(test_videos)} 条视频测试数据!")
        
        # 验证插入结果
        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE type = 'video'")
        video_count = cursor.fetchone()[0]
        print(f"📊 数据库中视频记录总数: {video_count}")
        
        # 显示最新插入的视频数据
        cursor.execute(f"""
        SELECT animal, location, type, caption 
        FROM {TABLE_NAME} 
        WHERE type = 'video' 
        ORDER BY time DESC 
        LIMIT 5
        """)
        
        recent_videos = cursor.fetchall()
        print("\n📹 最新的视频记录:")
        for video in recent_videos:
            print(f"   🎬 {video[0]} - {video[1]} ({video[2]})")
            print(f"      📝 {video[3]}")
        
    except mysql.connector.Error as e:
        print(f"❌ 数据库错误: {e}")
        if connection:
            connection.rollback()
    except Exception as e:
        print(f"❌ 其他错误: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        print("\n🔒 数据库连接已关闭")

def check_media_types():
    """检查数据库中的媒体类型分布"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # 统计不同媒体类型的数量
        cursor.execute(f"""
        SELECT type, COUNT(*) as count 
        FROM {TABLE_NAME} 
        GROUP BY type 
        ORDER BY count DESC
        """)
        
        type_stats = cursor.fetchall()
        print("📊 媒体类型统计:")
        total = 0
        for media_type, count in type_stats:
            print(f"   📁 {media_type}: {count} 条记录")
            total += count
        print(f"   📈 总计: {total} 条记录")
        
        # 按地点统计媒体类型
        cursor.execute(f"""
        SELECT location, type, COUNT(*) as count 
        FROM {TABLE_NAME} 
        GROUP BY location, type 
        ORDER BY location, type
        """)
        
        location_stats = cursor.fetchall()
        print("\n🗺️ 按地点的媒体类型分布:")
        current_location = None
        for location, media_type, count in location_stats:
            if location != current_location:
                print(f"   📍 {location}:")
                current_location = location
            print(f"      {media_type}: {count} 条")
        
    except mysql.connector.Error as e:
        print(f"❌ 数据库错误: {e}")
    except Exception as e:
        print(f"❌ 其他错误: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == "__main__":
    print("🎬 视频数据测试脚本")
    print("=" * 50)
    
    # 检查当前媒体类型分布
    print("1️⃣ 检查当前数据库状态...")
    check_media_types()
    
    print("\n" + "=" * 50)
    
    # 插入测试视频数据
    print("2️⃣ 插入测试视频数据...")
    insert_test_video_data()
    
    print("\n" + "=" * 50)
    
    # 再次检查媒体类型分布
    print("3️⃣ 检查更新后的数据库状态...")
    check_media_types()
    
    print("\n🎯 测试完成!")
    print("💡 现在可以在Web界面中测试视频显示功能了")
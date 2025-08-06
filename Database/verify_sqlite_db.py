#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLite数据库验证脚本
验证image_info.db数据库的内容和结构
"""

import sqlite3
import os

def verify_sqlite_database():
    """
    验证SQLite数据库
    """
    db_path = os.path.join(os.path.dirname(__file__), 'image_info.db')
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    print(f"🔍 验证SQLite数据库: {db_path}")
    print("=" * 60)
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取表信息
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"📋 数据库中的表: {[table[0] for table in tables]}")
        
        # 获取image_info表的结构
        cursor.execute("PRAGMA table_info(image_info);")
        columns = cursor.fetchall()
        print(f"\n📊 image_info表结构:")
        print("-" * 60)
        for col in columns:
            col_id, name, data_type, not_null, default_val, pk = col
            null_info = "NOT NULL" if not_null else "NULL"
            print(f"字段: {name:<15} 类型: {data_type:<15} 约束: {null_info}")
        
        # 统计数据
        cursor.execute("SELECT COUNT(*) FROM image_info")
        total_count = cursor.fetchone()[0]
        print(f"\n📊 总记录数: {total_count}")
        
        # 媒体类型统计
        cursor.execute("SELECT type, COUNT(*) FROM image_info GROUP BY type ORDER BY COUNT(*) DESC")
        type_stats = cursor.fetchall()
        print(f"\n📊 媒体类型分布:")
        for media_type, count in type_stats:
            print(f"   {media_type}: {count} 条")
        
        # 地点统计
        cursor.execute("SELECT location, COUNT(*) FROM image_info GROUP BY location ORDER BY COUNT(*) DESC")
        location_stats = cursor.fetchall()
        print(f"\n📊 地点分布:")
        for location, count in location_stats:
            print(f"   {location}: {count} 条")
        
        # 动物统计
        cursor.execute("SELECT animal, COUNT(*) FROM image_info GROUP BY animal ORDER BY COUNT(*) DESC")
        animal_stats = cursor.fetchall()
        print(f"\n📊 动物分布:")
        for animal, count in animal_stats:
            print(f"   {animal}: {count} 条")
        
        # 显示最新的5条记录
        cursor.execute("SELECT animal, location, type, date, time FROM image_info ORDER BY date DESC, time DESC LIMIT 5")
        recent_data = cursor.fetchall()
        print(f"\n📋 最新5条记录:")
        print("-" * 60)
        for i, (animal, location, media_type, date, time) in enumerate(recent_data, 1):
            print(f"   {i}. {animal} | {location} | {media_type} | {date} {time}")
        
        # 关闭连接
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ SQLite数据库验证完成!")
        return True
        
    except Exception as e:
        print(f"❌ 验证过程中发生错误: {e}")
        return False

if __name__ == "__main__":
    verify_sqlite_database()
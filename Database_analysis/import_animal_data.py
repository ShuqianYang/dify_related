#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据导入脚本
将animal_info.jsonl文件中的数据导入到image_info.db数据库中
"""

import sqlite3
import json
import os
from datetime import datetime

def import_animal_data():
    """
    将animal_info.jsonl数据导入到image_info.db数据库
    """
    # 获取文件路径
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.dirname(current_dir)
    database_dir = os.path.join(parent_dir, 'Database')
    
    db_path = os.path.join(database_dir, 'image_info.db')
    jsonl_path = os.path.join(database_dir, 'animal_info.jsonl')
    
    # 检查文件是否存在
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        print("💡 请先运行 create_image_info_db.py 创建数据库")
        return False
    
    if not os.path.exists(jsonl_path):
        print(f"❌ JSONL文件不存在: {jsonl_path}")
        return False
    
    print(f"📂 数据库路径: {db_path}")
    print(f"📂 JSONL文件路径: {jsonl_path}")
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='image_info';")
        if not cursor.fetchone():
            print("❌ image_info表不存在，请先创建数据库")
            conn.close()
            return False
        
        # 清空现有数据（可选）
        user_input = input("⚠️  是否要清空现有数据后导入? (y/N): ")
        if user_input.lower() in ['y', 'yes']:
            cursor.execute("DELETE FROM image_info")
            print("🗑️  已清空现有数据")
        
        # 读取并导入JSONL数据
        imported_count = 0
        error_count = 0
        
        print("\n🚀 开始导入数据...")
        
        with open(jsonl_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    # 解析JSON数据
                    data = json.loads(line)
                    
                    # 准备插入数据的SQL语句
                    insert_sql = """
                    INSERT INTO image_info (
                        object, animal, count, behavior, status, 
                        location, longitude, latitude, time, date, caption
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    
                    # 提取数据字段
                    values = (
                        data.get('object', ''),
                        data.get('animal', ''),
                        data.get('count', 0),
                        data.get('behavior', ''),
                        data.get('status', ''),
                        data.get('location', ''),
                        data.get('longitude', ''),
                        data.get('latitude', ''),
                        data.get('time', ''),
                        data.get('date', ''),
                        data.get('caption', '')
                    )
                    
                    # 执行插入
                    cursor.execute(insert_sql, values)
                    imported_count += 1
                    
                    # 每100条记录显示一次进度
                    if imported_count % 100 == 0:
                        print(f"📊 已导入 {imported_count} 条记录...")
                
                except json.JSONDecodeError as e:
                    print(f"⚠️  第 {line_num} 行JSON解析错误: {e}")
                    error_count += 1
                    continue
                except Exception as e:
                    print(f"⚠️  第 {line_num} 行数据插入错误: {e}")
                    error_count += 1
                    continue
        
        # 提交事务
        conn.commit()
        
        # 显示导入结果
        print("\n" + "=" * 60)
        print("📊 数据导入完成!")
        print(f"✅ 成功导入: {imported_count} 条记录")
        if error_count > 0:
            print(f"⚠️  错误记录: {error_count} 条")
        
        # 验证导入结果
        cursor.execute("SELECT COUNT(*) FROM image_info")
        total_count = cursor.fetchone()[0]
        print(f"📈 数据库总记录数: {total_count}")
        
        # 显示一些统计信息
        print("\n📊 数据统计:")
        print("-" * 40)
        
        # 按动物类型统计
        cursor.execute("SELECT animal, COUNT(*) FROM image_info GROUP BY animal ORDER BY COUNT(*) DESC")
        animal_stats = cursor.fetchall()
        print("🐾 动物类型统计:")
        for animal, count in animal_stats:
            print(f"  {animal}: {count} 条记录")
        
        # 按行为统计
        cursor.execute("SELECT behavior, COUNT(*) FROM image_info GROUP BY behavior ORDER BY COUNT(*) DESC LIMIT 10")
        behavior_stats = cursor.fetchall()
        print("\n🎭 行为统计 (前10):")
        for behavior, count in behavior_stats:
            print(f"  {behavior}: {count} 条记录")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 导入过程中发生错误: {e}")
        return False

def verify_import():
    """
    验证导入的数据
    """
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.dirname(current_dir)
    database_dir = os.path.join(parent_dir, 'Database')
    db_path = os.path.join(database_dir, 'image_info.db')
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n🔍 验证导入数据:")
        print("-" * 40)
        
        # 显示前5条记录
        cursor.execute("SELECT * FROM image_info LIMIT 5")
        records = cursor.fetchall()
        
        if records:
            print("📋 前5条记录:")
            for i, record in enumerate(records, 1):
                print(f"  记录 {i}: ID={record[0]}, 动物={record[2]}, 行为={record[4]}, 数量={record[3]}")
        else:
            print("❌ 没有找到任何记录")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 验证过程中发生错误: {e}")
        return False

def main():
    """
    主函数
    """
    print("🚀 动物数据导入工具")
    print("=" * 60)
    
    # 导入数据
    success = import_animal_data()
    
    if success:
        # 验证导入结果
        verify_import()
        
        print("\n" + "=" * 60)
        print("✅ 数据导入完成!")
        print("💡 现在可以使用数据库进行查询和分析")
    else:
        print("\n❌ 数据导入失败")

if __name__ == "__main__":
    main()
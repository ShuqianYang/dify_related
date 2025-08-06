#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MySQL到SQLite数据迁移脚本
将MySQL dify_test库中的image_info表数据迁移到已存在的SQLite数据库中

使用前提：
1. 需要先运行 init_sqlite_db.py 创建SQLite数据库和表结构
2. 确保MySQL数据库连接正常
3. 确保有足够的权限访问MySQL数据库

功能：
- 从MySQL读取image_info表的所有数据
- 将数据插入到SQLite数据库中
- 提供数据验证和统计功能
"""

import sqlite3
import pymysql
import os
import sys
from datetime import datetime

# 添加父目录到路径，以便导入db_config
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ECharts_map'))
from db_config import get_db_config, get_table_name

def connect_sqlite_database():
    """
    连接到已存在的SQLite数据库
    """
    db_path = os.path.join(os.path.dirname(__file__), 'image_info.db')
    
    # 检查数据库文件是否存在
    if not os.path.exists(db_path):
        print(f"❌ SQLite数据库文件不存在: {db_path}")
        print("💡 请先运行 init_sqlite_db.py 来创建数据库")
        return None, None
    
    try:
        # 连接SQLite数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查image_info表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='image_info';")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print(f"❌ image_info表不存在于数据库中")
            print("💡 请先运行 init_sqlite_db.py 来创建表结构")
            conn.close()
            return None, None
        
        print(f"✅ 成功连接到SQLite数据库: {db_path}")
        
        # 检查当前记录数
        cursor.execute("SELECT COUNT(*) FROM image_info")
        current_count = cursor.fetchone()[0]
        if current_count > 0:
            user_input = input(f"⚠️  数据库中已有 {current_count} 条记录，是否要清空后重新导入? (y/N): ")
            if user_input.lower() in ['y', 'yes']:
                cursor.execute("DELETE FROM image_info")
                conn.commit()
                print("🗑️  已清空现有数据")
            else:
                print("💡 将在现有数据基础上追加新数据")
        
        return conn, db_path
        
    except Exception as e:
        print(f"❌ 连接SQLite数据库失败: {e}")
        return None, None

def get_sqlite_table_structure(sqlite_conn):
    """
    获取SQLite表结构
    """
    cursor = sqlite_conn.cursor()
    cursor.execute("PRAGMA table_info(image_info);")
    columns_info = cursor.fetchall()
    
    # 返回字段名列表（排除自增主键id）
    sqlite_columns = []
    for col in columns_info:
        col_id, name, data_type, not_null, default_val, pk = col
        if name != 'id':  # 排除自增主键
            sqlite_columns.append(name)
    
    return sqlite_columns

def migrate_data_from_mysql(sqlite_conn):
    """
    从MySQL数据库迁移数据到SQLite
    """
    # 获取MySQL配置
    mysql_config = get_db_config()
    table_name = get_table_name()
    
    try:
        # 连接MySQL数据库
        mysql_conn = pymysql.connect(**mysql_config)
        mysql_cursor = mysql_conn.cursor()
        
        print(f"✅ 成功连接到MySQL数据库: {mysql_config['database']}")
        
        # 获取SQLite表结构
        sqlite_columns = get_sqlite_table_structure(sqlite_conn)
        print(f"📋 SQLite表字段: {', '.join(sqlite_columns)}")
        
        # 查询MySQL数据，只选择SQLite表中存在的字段
        mysql_cursor.execute(f"DESCRIBE {table_name}")
        mysql_table_info = mysql_cursor.fetchall()
        mysql_columns = [col[0] for col in mysql_table_info]
        print(f"📋 MySQL表字段: {', '.join(mysql_columns)}")
        
        # 找出两个表的共同字段
        common_columns = []
        for col in sqlite_columns:
            if col in mysql_columns:
                common_columns.append(col)
        
        print(f"📋 共同字段: {', '.join(common_columns)}")
        
        if not common_columns:
            print("❌ 没有找到共同字段，无法进行数据迁移")
            return False
        
        # 查询MySQL数据
        select_sql = f"SELECT {', '.join(common_columns)} FROM {table_name}"
        mysql_cursor.execute(select_sql)
        
        # 获取所有数据
        rows = mysql_cursor.fetchall()
        print(f"📊 找到 {len(rows)} 条记录")
        
        if len(rows) == 0:
            print("⚠️  MySQL表中没有数据")
            mysql_cursor.close()
            mysql_conn.close()
            return True
        
        # 准备SQLite插入语句
        placeholders = ', '.join(['?' for _ in common_columns])
        insert_sql = f"INSERT INTO image_info ({', '.join(common_columns)}) VALUES ({placeholders})"
        print(f"📝 插入SQL: {insert_sql}")
        
        # 插入数据到SQLite
        sqlite_cursor = sqlite_conn.cursor()
        
        success_count = 0
        error_count = 0
        
        for row in rows:
            try:
                # 数据预处理：处理None值和数据类型转换
                processed_row = []
                for i, value in enumerate(row):
                    col_name = common_columns[i]
                    
                    # 处理必填字段的None值
                    if value is None:
                        if col_name in ['object', 'animal']:
                            processed_row.append('未知')
                        elif col_name in ['count', 'percentage', 'confidence']:
                            processed_row.append(0)
                        else:
                            processed_row.append('')
                    else:
                        processed_row.append(value)
                
                sqlite_cursor.execute(insert_sql, processed_row)
                success_count += 1
                
            except Exception as e:
                print(f"❌ 插入数据失败: {e}")
                print(f"   数据: {row}")
                error_count += 1
        
        # 提交事务
        sqlite_conn.commit()
        
        print(f"✅ 数据迁移完成!")
        print(f"   成功插入: {success_count} 条记录")
        if error_count > 0:
            print(f"   失败: {error_count} 条记录")
        
        # 关闭MySQL连接
        mysql_cursor.close()
        mysql_conn.close()
        
    except Exception as e:
        print(f"❌ MySQL连接或数据迁移失败: {e}")
        return False
    
    return True

def verify_migration(sqlite_conn):
    """
    验证迁移结果
    """
    cursor = sqlite_conn.cursor()
    
    # 获取表结构信息
    cursor.execute("PRAGMA table_info(image_info);")
    columns_info = cursor.fetchall()
    available_columns = [col[1] for col in columns_info]
    
    # 统计总记录数
    cursor.execute("SELECT COUNT(*) FROM image_info")
    total_count = cursor.fetchone()[0]
    print(f"📊 SQLite数据库中总记录数: {total_count}")
    
    # 显示表结构
    print(f"📋 表结构: {', '.join(available_columns)}")
    
    # 统计不同媒体类型（如果type字段存在）
    if 'type' in available_columns:
        try:
            cursor.execute("SELECT type, COUNT(*) FROM image_info WHERE type IS NOT NULL AND type != '' GROUP BY type")
            type_stats = cursor.fetchall()
            if type_stats:
                print("📊 媒体类型统计:")
                for media_type, count in type_stats:
                    print(f"   {media_type}: {count} 条")
        except Exception as e:
            print(f"⚠️  媒体类型统计失败: {e}")
    
    # 统计不同地点（如果location字段存在）
    if 'location' in available_columns:
        try:
            cursor.execute("SELECT location, COUNT(*) FROM image_info WHERE location IS NOT NULL AND location != '' GROUP BY location")
            location_stats = cursor.fetchall()
            if location_stats:
                print("📊 地点分布统计:")
                for location, count in location_stats:
                    print(f"   {location}: {count} 条")
        except Exception as e:
            print(f"⚠️  地点统计失败: {e}")
    
    # 统计不同动物（如果animal字段存在）
    if 'animal' in available_columns:
        try:
            cursor.execute("SELECT animal, COUNT(*) FROM image_info WHERE animal IS NOT NULL AND animal != '' GROUP BY animal")
            animal_stats = cursor.fetchall()
            if animal_stats:
                print("📊 动物分布统计:")
                for animal, count in animal_stats:
                    print(f"   {animal}: {count} 条")
        except Exception as e:
            print(f"⚠️  动物统计失败: {e}")
    
    # 显示前3条记录作为样本
    try:
        # 构建查询语句，只选择存在的字段
        sample_fields = []
        for field in ['id', 'animal', 'location', 'type', 'date']:
            if field in available_columns:
                sample_fields.append(field)
        
        if sample_fields:
            query = f"SELECT {', '.join(sample_fields)} FROM image_info LIMIT 3"
            cursor.execute(query)
            sample_data = cursor.fetchall()
            print("📋 样本数据:")
            for i, row in enumerate(sample_data, 1):
                row_info = []
                for j, field in enumerate(sample_fields):
                    row_info.append(f"{field}: {row[j]}")
                print(f"   {i}. {' | '.join(row_info)}")
    except Exception as e:
        print(f"⚠️  样本数据显示失败: {e}")

def main():
    """
    主函数
    """
    print("🚀 开始MySQL到SQLite数据迁移...")
    print("=" * 60)
    
    try:
        # 连接到SQLite数据库
        sqlite_conn, db_path = connect_sqlite_database()
        
        if sqlite_conn is None:
            return False
        
        # 迁移数据
        if migrate_data_from_mysql(sqlite_conn):
            print("\n" + "=" * 60)
            print("🔍 验证迁移结果:")
            verify_migration(sqlite_conn)
        
        # 关闭SQLite连接
        sqlite_conn.close()
        
        print("\n" + "=" * 60)
        print(f"✅ 迁移完成! SQLite数据库位置: {db_path}")
        
    except Exception as e:
        print(f"❌ 迁移过程中发生错误: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
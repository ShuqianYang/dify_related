#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import pymysql

sys.path.append('ECharts_map')  # 运行系统路径改为'ECharts_map'
from db_config import get_db_config, get_table_name

def check_table_structure():
    """检查数据库表结构"""
    try:
        # 连接数据库
        connection = pymysql.connect(**get_db_config())
        cursor = connection.cursor()
        
        table_name = get_table_name()
        print(f"🔍 检查表 '{table_name}' 的结构:")
        
        # 查看表结构
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        
        print("\n📋 表字段信息:")
        print("-" * 60)
        for column in columns:
            field, type_, null, key, default, extra = column
            print(f"字段: {field:<15} 类型: {type_:<20} 允许NULL: {null}")
        
        # 查看前几条数据
        print(f"\n📊 表 '{table_name}' 的前5条数据:")
        print("-" * 80)
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
        rows = cursor.fetchall()
        
        if rows:
            # 获取列名
            cursor.execute(f"SHOW COLUMNS FROM {table_name}")
            column_info = cursor.fetchall()
            column_names = [col[0] for col in column_info]
            
            print("列名:", " | ".join(f"{name:<12}" for name in column_names))
            print("-" * 80)
            
            for row in rows:
                print(" | ".join(f"{str(val):<12}" for val in row))
        else:
            print("表中没有数据")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ 检查数据库结构时出错: {e}")

if __name__ == "__main__":
    check_table_structure()
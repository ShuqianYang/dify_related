#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import pymysql

sys.path.append('ECharts_map')
from db_config import get_db_config, get_table_name

def check_real_image_paths():
    """检查数据库中实际的图片路径"""
    conn = pymysql.connect(**get_db_config())
    cursor = conn.cursor()
    
    try:
        # 首先查看表结构
        table_name = get_table_name()
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        print(f'{table_name}表结构:')
        print('字段名 | 类型 | 是否为空 | 键 | 默认值 | 额外')
        print('-' * 80)
        
        for column in columns:
            print(f'{column[0]:<15} | {column[1]:<15} | {column[2]:<8} | {column[3]:<5} | {str(column[4]):<10} | {column[5]}')
        
        # 查询所有有图片路径的记录
        cursor.execute(f"SELECT DISTINCT animal, path FROM {table_name} WHERE path IS NOT NULL AND path != '' LIMIT 20")
        results = cursor.fetchall()
        
        print('\n' + '='*80)
        print('数据库中实际的图片路径:')
        print('动物类型 | 图片路径')
        print('-' * 80)
        
        if results:
            for animal, path in results:
                print(f'{animal:<15} | {path}')
        else:
            print('没有找到有效的图片路径记录')
            
        # 查询所有记录的path字段情况
        print('\n' + '='*80)
        print('所有记录的path字段统计:')
        cursor.execute("SELECT COUNT(*) as total, COUNT(path) as has_path, COUNT(CASE WHEN path IS NOT NULL AND path != '' THEN 1 END) as valid_path FROM image_info")
        stats = cursor.fetchone()
        print(f'总记录数: {stats[0]}')
        print(f'有path字段的记录数: {stats[1]}')
        print(f'有效path字段的记录数: {stats[2]}')
        
        # 查看前几条记录的详细信息
        print('\n' + '='*80)
        print('前5条记录的详细信息:')
        cursor.execute("SELECT animal, caption, path FROM image_info LIMIT 5")
        sample_results = cursor.fetchall()
        for i, (animal, caption, path) in enumerate(sample_results, 1):
            print(f'{i}. 动物: {animal}, 描述: {caption[:30] if caption else "无"}..., 路径: {path}')
            
    except Exception as e:
        print(f'查询错误: {e}')
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    check_real_image_paths()
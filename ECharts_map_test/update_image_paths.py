#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'ECharts_map'))

import pymysql
from ECharts_map.db_config import get_db_config, get_table_name

def update_image_paths():
    """更新数据库中的图片路径"""
    try:
        # 连接数据库
        connection = pymysql.connect(**get_db_config())
        cursor = connection.cursor()
        
        table_name = get_table_name()
        print(f"🔄 更新表 '{table_name}' 中的图片路径...")
        
        # 定义动物与图片的映射关系
        animal_image_mapping = {
            '熊猫': '/static/images/panda_001.svg',
            '大熊猫': '/static/images/panda_001.svg',
            '华南虎': '/static/images/tiger_001.svg',
            '老虎': '/static/images/tiger_001.svg',
            '金丝猴': '/static/images/monkey_001.svg',
            '猴子': '/static/images/monkey_001.svg',
            '猴': '/static/images/monkey_001.svg'
        }
        
        # 更新每种动物的图片路径
        for animal, image_path in animal_image_mapping.items():
            update_sql = f"""
            UPDATE {table_name} 
            SET path = %s 
            WHERE animal = %s AND (path IS NULL OR path = '')
            """
            
            cursor.execute(update_sql, (image_path, animal))
            affected_rows = cursor.rowcount
            print(f"✅ 更新 '{animal}' 的图片路径: {image_path} (影响 {affected_rows} 行)")
        
        # 为其他动物设置默认图片路径（基于动物名称）
        default_update_sql = f"""
        UPDATE {table_name} 
        SET path = CONCAT('/static/images/', LOWER(animal), '_001.svg')
        WHERE path IS NULL OR path = ''
        """
        
        cursor.execute(default_update_sql)
        affected_rows = cursor.rowcount
        print(f"🔧 为其他动物设置默认图片路径 (影响 {affected_rows} 行)")
        
        # 提交更改
        connection.commit()
        
        # 验证更新结果
        print(f"\n📊 验证更新结果:")
        print("-" * 60)
        
        verify_sql = f"""
        SELECT animal, path, COUNT(*) as count 
        FROM {table_name} 
        WHERE path IS NOT NULL AND path != ''
        GROUP BY animal, path
        ORDER BY animal
        """
        
        cursor.execute(verify_sql)
        results = cursor.fetchall()
        
        for animal, path, count in results:
            print(f"动物: {animal:<10} 图片路径: {path:<30} 记录数: {count}")
        
        cursor.close()
        connection.close()
        
        print(f"\n✅ 图片路径更新完成！")
        
    except Exception as e:
        print(f"❌ 更新图片路径时出错: {e}")

if __name__ == "__main__":
    update_image_paths()
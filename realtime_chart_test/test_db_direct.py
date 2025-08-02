#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
from realtime_chart.db_config import get_db_config

def test_database_direct():
    """直接测试数据库连接和数据"""
    print("=== 直接数据库查询测试 ===\n")
    
    try:
        # 连接数据库
        connection = pymysql.connect(**get_db_config())
        print("✅ 数据库连接成功")
        
        with connection.cursor() as cursor:
            # 1. 检查表结构
            print("\n1. 检查表结构:")
            cursor.execute("DESCRIBE image_info")
            columns = cursor.fetchall()
            for col in columns:
                print(f"   {col[0]}: {col[1]}")
            
            # 2. 检查总记录数
            print("\n2. 总记录数:")
            cursor.execute("SELECT COUNT(*) FROM image_info")
            total = cursor.fetchone()[0]
            print(f"   总记录数: {total}")
            
            # 3. 检查动物种类分布
            print("\n3. 动物种类分布:")
            cursor.execute("SELECT animal, COUNT(*) as count FROM image_info GROUP BY animal ORDER BY count DESC")
            animals = cursor.fetchall()
            for animal, count in animals:
                print(f"   {animal}: {count} 条记录")
            
            # 4. 检查时间字段格式
            print("\n4. 时间字段样本:")
            cursor.execute("SELECT animal, time, date FROM image_info LIMIT 5")
            samples = cursor.fetchall()
            for animal, time, date in samples:
                print(f"   动物: {animal}, 时间: {time}, 日期: {date}")
            
            # 5. 测试活动时间查询
            print("\n5. 测试活动时间查询:")
            
            # 先查看时间样本
            cursor.execute("SELECT DISTINCT time FROM image_info WHERE time IS NOT NULL AND time != '' LIMIT 10")
            time_samples = cursor.fetchall()
            print("   时间样本:")
            for (time_val,) in time_samples:
                print(f"     '{time_val}'")
            
            # 尝试不同的解析方法
            print("\n   尝试方法1: 直接使用SUBSTRING提取小时")
            try:
                cursor.execute("""
                SELECT 
                    CAST(SUBSTRING(time, 1, 2) AS UNSIGNED) as hour,
                    COUNT(*) as count
                FROM image_info 
                WHERE time IS NOT NULL AND time != '' AND time LIKE '__:__'
                GROUP BY CAST(SUBSTRING(time, 1, 2) AS UNSIGNED)
                ORDER BY hour;
                """)
                activity_data = cursor.fetchall()
                if activity_data:
                    print("   ✅ 活动时间分布:")
                    for hour, count in activity_data:
                        print(f"   - {hour}:00 时段: {count} 次")
                else:
                    print("   ⚠️  没有有效的时间数据")
            except Exception as e:
                print(f"   ❌ 方法1失败: {e}")
            
            print("\n   尝试方法2: 使用TIME函数")
            try:
                cursor.execute("""
                SELECT 
                    HOUR(TIME(time)) as hour,
                    COUNT(*) as count
                FROM image_info 
                WHERE time IS NOT NULL AND time != ''
                GROUP BY HOUR(TIME(time))
                ORDER BY hour;
                """)
                activity_data = cursor.fetchall()
                if activity_data:
                    print("   ✅ 活动时间分布:")
                    for hour, count in activity_data:
                        print(f"   - {hour}:00 时段: {count} 次")
                else:
                    print("   ⚠️  没有有效的时间数据")
            except Exception as e:
                print(f"   ❌ 方法2失败: {e}")
        
        connection.close()
        print("\n✅ 数据库测试完成")
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")

if __name__ == "__main__":
    test_database_direct()
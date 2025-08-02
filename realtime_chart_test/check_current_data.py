#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 检查当前数据状态

import requests

def check_current_data():
    """检查当前数据状态"""
    base_url = "http://127.0.0.1:5003"
    
    print("=== 检查当前数据库状态 ===\n")
    
    # 1. 检查动物种类分布
    print("1. 动物种类分布数据:")
    try:
        response = requests.get(f"{base_url}/api/chart-data")
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                animals = data.get('data', [])
                print(f"   总共 {len(animals)} 种动物:")
                for animal in animals:
                    print(f"   - {animal['animal']}: {animal['count']} 条记录")
            else:
                print(f"   ❌ 错误: {data.get('message')}")
        else:
            print(f"   ❌ HTTP错误: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 2. 检查动物列表
    print("\n2. 动物列表:")
    try:
        response = requests.get(f"{base_url}/api/animal-list")
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                animals = data.get('data', [])
                print(f"   动物种类: {animals}")
            else:
                print(f"   ❌ 错误: {data.get('message')}")
        else:
            print(f"   ❌ HTTP错误: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 3. 检查活动时间分布（所有动物）
    print("\n3. 活动时间分布数据（所有动物）:")
    try:
        response = requests.get(f"{base_url}/api/activity-data")
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                activity_data = data.get('data', {})
                # 找出有活动的时间段
                active_hours = {hour: count for hour, count in activity_data.items() if count > 0}
                if active_hours:
                    print(f"   有活动的时间段:")
                    for hour, count in active_hours.items():
                        print(f"   - {hour}:00 时段: {count} 次活动")
                else:
                    print("   ⚠️  所有时间段都没有活动记录")
            else:
                print(f"   ❌ 错误: {data.get('message')}")
        else:
            print(f"   ❌ HTTP错误: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 4. 检查时间序列数据
    print("\n4. 时间序列数据:")
    try:
        response = requests.get(f"{base_url}/api/timeseries-data")
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                timeseries = data.get('data', [])
                print(f"   时间序列记录数: {len(timeseries)}")
                for record in timeseries[:3]:  # 显示前3条
                    print(f"   - 日期: {record.get('date')}, 数量: {record.get('count')}")
            else:
                print(f"   ❌ 错误: {data.get('message')}")
        else:
            print(f"   ❌ HTTP错误: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")

if __name__ == "__main__":
    check_current_data()
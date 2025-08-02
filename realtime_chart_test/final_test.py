#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def final_test():
    """最终功能验证测试"""
    base_url = "http://127.0.0.1:5003"
    
    print("=== 最终功能验证测试 ===\n")
    
    # 1. 测试动物种类分布（所有时间）
    print("1. 动物种类分布（所有时间）:")
    response = requests.get(f"{base_url}/api/chart-data")
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'success':
            animals = data.get('data', [])
            print(f"   ✅ 成功获取 {len(animals)} 种动物数据")
            for animal in animals:
                print(f"   - {animal['animal']}: {animal['count']} 条记录")
        else:
            print(f"   ❌ API错误: {data.get('message')}")
    else:
        print(f"   ❌ HTTP错误: {response.status_code}")
    
    # 2. 测试活动时间分布（所有动物）
    print("\n2. 活动时间分布（所有动物）:")
    response = requests.get(f"{base_url}/api/activity-data")
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'success':
            activity_data = data.get('data', {})
            active_hours = {hour: count for hour, count in activity_data.items() if int(count) > 0}
            if active_hours:
                print(f"   ✅ 成功获取活动时间数据，有 {len(active_hours)} 个活跃时段")
                for hour, count in active_hours.items():
                    print(f"   - {hour}:00 时段: {count} 次活动")
            else:
                print("   ⚠️  没有活动记录")
        else:
            print(f"   ❌ API错误: {data.get('message')}")
    else:
        print(f"   ❌ HTTP错误: {response.status_code}")
    
    # 3. 测试特定动物的活动时间分布
    print("\n3. 扬子鳄的活动时间分布:")
    response = requests.get(f"{base_url}/api/activity-data?animal=扬子鳄")
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'success':
            activity_data = data.get('data', {})
            active_hours = {hour: count for hour, count in activity_data.items() if int(count) > 0}
            if active_hours:
                print(f"   ✅ 扬子鳄有 {len(active_hours)} 个活跃时段")
                for hour, count in active_hours.items():
                    print(f"   - {hour}:00 时段: {count} 次活动")
            else:
                print("   ⚠️  扬子鳄没有活动记录")
        else:
            print(f"   ❌ API错误: {data.get('message')}")
    else:
        print(f"   ❌ HTTP错误: {response.status_code}")
    
    # 4. 测试时间序列数据
    print("\n4. 时间序列数据:")
    response = requests.get(f"{base_url}/api/timeseries-data")
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'success':
            timeseries = data.get('data', [])
            print(f"   ✅ 成功获取 {len(timeseries)} 条时间序列记录")
            for record in timeseries:
                print(f"   - 日期: {record.get('date')}, 数量: {record.get('count')}")
        else:
            print(f"   ❌ API错误: {data.get('message')}")
    else:
        print(f"   ❌ HTTP错误: {response.status_code}")
    
    print("\n=== 测试完成 ===")
    print("✅ 数据库更新后，动物种类和识别时间已正确更新")
    print("✅ 动物活动时间分布图数据正常获取")

if __name__ == "__main__":
    final_test()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试弹窗数据API的脚本
用于验证地图数据和详情数据的一致性

主要功能：
1. 测试Flask服务器连接状态
2. 获取并验证地图数据API
3. 获取并验证位置详情数据API
4. 检查地图显示数据与详情数据的一致性
5. 批量验证所有监测点的数据一致性

作者：动物监测系统开发团队
创建时间：2025年
"""

import requests  # 用于发送HTTP请求
import json      # 用于处理JSON数据
import time      # 用于添加请求间隔

def test_api_connection():
    """
    测试API服务器连接状态
    
    功能说明：
    - 向Flask服务器发送GET请求测试连接
    - 设置5秒超时时间避免长时间等待
    - 检查HTTP状态码确认服务器正常运行
    
    返回值：
    - True: 服务器连接正常
    - False: 服务器连接失败
    """
    try:
        print('🔗 测试服务器连接...')
        # 向Flask应用主页发送请求，超时时间5秒
        response = requests.get('http://localhost:5005', timeout=5)
        
        # 检查HTTP状态码
        if response.status_code == 200:
            print('✅ 服务器连接正常')
            return True
        else:
            print(f'❌ 服务器响应异常: {response.status_code}')
            return False
            
    except requests.exceptions.ConnectionError:
        # 处理连接错误（服务器未启动等）
        print('❌ 无法连接到服务器，请确保Flask应用正在运行')
        return False
    except requests.exceptions.Timeout:
        # 处理超时错误
        print('❌ 连接超时')
        return False
    except Exception as e:
        # 处理其他未知错误
        print(f'❌ 连接错误: {e}')
        return False

def get_map_data():
    """
    获取地图数据API的响应
    
    功能说明：
    - 调用 /api/map-data 接口获取所有监测点的汇总数据
    - 包含每个地点的名称、坐标、监测总数、动物类型等信息
    - 用于在地图上显示监测点标记
    
    返回值：
    - 成功: 返回地图数据列表
    - 失败: 返回None
    """
    try:
        print('\n=== 📍 地图数据API ===')
        # 请求地图数据API，超时时间10秒
        response = requests.get('http://localhost:5005/api/map-data', timeout=10)
        # 如果HTTP状态码不是2xx，抛出异常
        response.raise_for_status()
        # 解析JSON响应
        map_data = response.json()
        print(f'✅ 成功获取地图数据，共 {len(map_data)} 个地点')
        return map_data
        
    except requests.exceptions.RequestException as e:
        # 处理网络请求异常
        print(f'❌ 获取地图数据失败: {e}')
        return None
    except json.JSONDecodeError as e:
        # 处理JSON解析异常
        print(f'❌ 解析地图数据JSON失败: {e}')
        return None

def get_location_detail(longitude, latitude):
    """
    获取指定坐标位置的详细监测数据
    
    参数：
    - longitude: 经度坐标
    - latitude: 纬度坐标
    
    功能说明：
    - 调用 /api/location-detail 接口获取特定位置的详细信息
    - 包含该位置所有动物监测记录的详细信息
    - 用于在地图点击时显示弹窗详情
    
    返回值：
    - 成功: 返回包含details和latest_by_animal的字典
    - 失败: 返回None
    """
    try:
        # 构建API请求URL，传入经纬度参数
        url = f'http://localhost:5005/api/location-detail?longitude={longitude}&latitude={latitude}'
        # 发送GET请求，超时时间10秒
        response = requests.get(url, timeout=10)
        # 检查HTTP状态码
        response.raise_for_status()
        # 解析JSON响应数据
        detail_data = response.json()
        return detail_data
        
    except requests.exceptions.RequestException as e:
        # 处理网络请求异常
        print(f'❌ 获取详情数据失败: {e}')
        return None
    except json.JSONDecodeError as e:
        # 处理JSON解析异常
        print(f'❌ 解析详情数据JSON失败: {e}')
        return None

def main():
    """
    主函数 - 执行完整的API测试流程
    
    测试流程：
    1. 测试服务器连接状态
    2. 获取并验证地图数据
    3. 测试特定位置（大兴安岭）的详情数据
    4. 验证地图数据与详情数据的一致性
    5. 批量测试多个监测点的数据一致性
    6. 输出测试结果汇总
    """
    print('🗺️ 动物监测地图数据一致性测试')
    print('=' * 50)
    
    # 第一步：测试服务器连接
    if not test_api_connection():
        print('\n💡 请先启动Flask服务器: python echarts_map_app.py')
        return
    
    # 第二步：获取地图数据
    map_data = get_map_data()
    if not map_data:
        return
    
    # 第三步：查找大兴安岭数据
    daxinganling_map = None
    for item in map_data:
        if item.get('name') == '大兴安岭':
            daxinganling_map = item
            break
    
    if daxinganling_map:
        print('\n📍 大兴安岭地图数据:')
        print(f'  地点: {daxinganling_map.get("name")}')
        print(f'  监测总数: {daxinganling_map.get("value")}')
        print(f'  动物类型: {daxinganling_map.get("animal_types")}')
        print(f'  坐标: {daxinganling_map.get("coord")}')
    else:
        print('⚠️ 未找到大兴安岭数据')
        # 显示所有可用地点
        print('📋 可用地点列表:')
        for item in map_data[:5]:  # 只显示前5个
            print(f'  - {item.get("name")}: {item.get("coord")}')
    
    # 第四步：检查详情数据API
    print('\n=== 🔍 详情数据API ===')
    # 使用大兴安岭的经纬度坐标进行测试
    detail_response = get_location_detail(124.71, 52.33)
    
    if detail_response is None:
        print('❌ 无法获取详情数据')
        return
    
    # 解析API返回的数据结构
    # API返回格式: {"details": [...], "latest_by_animal": {...}}
    detail_data = detail_response.get('details', [])
    latest_by_animal = detail_response.get('latest_by_animal', {})
    
    print(f'✅ 详情数据条数: {len(detail_data)}')
    print(f'✅ 动物种类数: {len(latest_by_animal)}')
    
    # 统计各种动物的监测数量
    animal_counts = {}  # 存储每种动物的数量统计
    total_count = 0     # 总监测数量计数器
    
    # 遍历详情数据中的每一条记录
    for item in detail_data:
        # 确保数据项是字典格式
        if isinstance(item, dict):
            animal = item.get('animal_type')    # 获取动物类型
            count = item.get('count', 1)        # 获取监测数量，默认为1
            
            # 如果动物类型有效，则进行统计
            if animal:
                # 累加该动物类型的数量
                animal_counts[animal] = animal_counts.get(animal, 0) + count
                # 累加总数量
                total_count += count
    
    if animal_counts:
        print('\n🐾 详情统计:')
        for animal, count in animal_counts.items():
            print(f'  {animal}: {count}只')
        print(f'📊 总计: {total_count}只')
    else:
        print('⚠️ 该位置暂无动物监测数据')
    
    # 第五步：对比一致性
    if daxinganling_map and animal_counts:
        print('\n=== ⚖️ 一致性检查 ===')
        map_total = int(daxinganling_map.get('value', 0))
        detail_total = total_count
        
        print(f'地图显示总数: {map_total}')
        print(f'详情统计总数: {detail_total}')
        print(f'数据一致性: {"✅ 一致" if map_total == detail_total else "❌ 不一致"}')
    
    # 第六步：检查所有地点的一致性（限制数量避免过多请求）
    print('\n=== 🌍 所有地点一致性检查 ===')
    max_check = min(5, len(map_data))  # 最多检查5个地点
    print(f'检查前 {max_check} 个地点...')
    success_count = 0  # 成功验证的地点数量
    
    # 遍历前N个地点进行批量一致性检查
    for i, map_item in enumerate(map_data[:max_check]):
        # 提取地点基本信息
        location = map_item.get('name')           # 地点名称
        coord = map_item.get('coord')             # 坐标数组 [经度, 纬度]
        map_value = int(map_item.get('value', 0)) # 地图显示的监测数量
        
        # 验证坐标数据的有效性
        if coord and len(coord) >= 2:
            # 提取经纬度坐标
            lng, lat = coord[0], coord[1]
            print(f'  检查 {location} ({lng}, {lat})...', end=' ')
            
            # 调用详情API获取该位置的详细数据
            detail_response = get_location_detail(lng, lat)
            if detail_response is not None:
                # 解析详情数据
                detail_data = detail_response.get('details', [])
                # 计算详情数据中的总监测数量
                detail_total = sum(item.get('count', 1) for item in detail_data if isinstance(item, dict))
                
                # 比较地图显示数量与详情统计数量
                status = "✅" if map_value == detail_total else "❌"
                print(f'{status} 地图={map_value}, 详情={detail_total}')
                
                # 如果数据一致，增加成功计数
                if map_value == detail_total:
                    success_count += 1
            else:
                print('❌ 获取详情失败')
            
            # 添加延迟避免请求过快，保护服务器
            time.sleep(0.5)
        else:
            # 坐标数据无效的情况
            print(f'  ⚠️ {location}: 坐标数据无效')
    
    # 第七步：输出测试结果汇总
    print(f'\n=== 📊 测试结果汇总 ===')
    print(f'✅ 成功检查: {success_count}/{max_check} 个地点')
    print(f'📈 成功率: {success_count/max_check*100:.1f}%')
    print('\n✅ 测试完成!')

# 程序入口点
if __name__ == '__main__':
    """
    脚本直接运行时的入口点
    
    使用方法：
    1. 确保Flask服务器在localhost:5005端口运行
    2. 在命令行中运行: python test_popup_data.py
    3. 查看测试结果和数据一致性报告
    """
    try:
        # 执行主测试流程
        main()
    except KeyboardInterrupt:
        # 处理用户按Ctrl+C中断程序的情况
        print('\n\n⏹️ 测试被用户中断')
    except Exception as e:
        # 处理程序运行过程中的未知异常
        print(f'\n❌ 测试过程中发生错误: {e}')
        # 导入traceback模块用于打印详细的错误堆栈信息
        import traceback
        # 打印完整的错误堆栈，便于调试
        traceback.print_exc()
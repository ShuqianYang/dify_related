import requests

try:
    # 1. 检查地图数据API
    print('=== 地图数据API ===')
    response = requests.get('http://localhost:5005/api/map-data')
    map_data = response.json()
    
    # 找到大兴安岭的数据
    daxinganling_map = None
    for item in map_data:
        if item.get('name') == '大兴安岭':
            daxinganling_map = item
            break
    
    if daxinganling_map:
        print('大兴安岭地图数据:')
        print(f'  地点: {daxinganling_map.get("name")}')
        print(f'  监测总数: {daxinganling_map.get("value")}')
        print(f'  动物类型: {daxinganling_map.get("animal_types")}')
        print(f'  坐标: {daxinganling_map.get("coord")}')
    else:
        print('未找到大兴安岭数据')
    
    print()
    
    # 2. 检查详情数据API
    print('=== 详情数据API ===')
    response = requests.get('http://localhost:5005/api/location-detail?longitude=124.71&latitude=52.33')
    detail_data = response.json()
    
    print(f'详情数据条数: {len(detail_data)}')
    
    # 统计动物数量
    animal_counts = {}
    total_count = 0
    for item in detail_data:
        animal = item.get('animal_type')
        count = item.get('count', 1)
        animal_counts[animal] = animal_counts.get(animal, 0) + count
        total_count += count
    
    print('详情统计:')
    for animal, count in animal_counts.items():
        print(f'  {animal}: {count}只')
    print(f'总计: {total_count}只')
    
    print()
    
    # 3. 对比一致性
    print('=== 一致性检查 ===')
    map_total = int(daxinganling_map.get('value', 0)) if daxinganling_map else 0
    detail_total = total_count
    
    print(f'地图显示总数: {map_total}')
    print(f'详情统计总数: {detail_total}')
    print(f'数据一致性: {"✅ 一致" if map_total == detail_total else "❌ 不一致"}')
    
    # 4. 检查所有地点的一致性
    print()
    print('=== 所有地点一致性检查 ===')
    for map_item in map_data:
        location = map_item.get('name')
        coord = map_item.get('coord')
        map_value = int(map_item.get('value', 0))
        
        if coord and len(coord) >= 2:
            lng, lat = coord[0], coord[1]
            detail_response = requests.get(f'http://localhost:5005/api/location-detail?longitude={lng}&latitude={lat}')
            detail_data = detail_response.json()
            
            detail_total = sum(item.get('count', 1) for item in detail_data)
            
            status = "✅" if map_value == detail_total else "❌"
            print(f'{status} {location}: 地图={map_value}, 详情={detail_total}')
    
except Exception as e:
    print('错误:', e)
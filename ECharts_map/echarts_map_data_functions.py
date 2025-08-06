# echarts_map_data_functions.py - ECharts地图数据获取功能合并文件
"""
本文件合并了以下功能模块：
1. get_animal_list.py - 动物列表和地点列表获取
2. get_map_data.py - 地图数据和位置详情获取

主要功能：
- get_animal_list(): 获取动物种类列表
- get_location_list(): 获取地点列表  
- get_map_data(): 获取地图数据点
- get_location_detail(): 获取位置详细信息

技术特点：
- 使用SQLite数据库连接
- 支持动物类型和日期筛选
- 处理带方向前缀的经纬度数据
- 返回结构化的JSON数据
"""

import sqlite3
from db_config import get_db_path, get_table_name

# ==================== 动物列表和地点列表功能 ====================

def get_animal_list():
    """
    获取所有动物种类列表
    
    Returns:
        list: 动物种类列表
    """
    try:
        # 连接SQLite数据库
        db_path = get_db_path()
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        table_name = get_table_name()
        sql = f"""
        SELECT DISTINCT animal
        FROM {table_name}
        WHERE animal IS NOT NULL AND animal != ''
        ORDER BY animal
        """
        
        cursor.execute(sql)
        results = cursor.fetchall()
        
        # 处理结果
        animal_list = [row[0] for row in results]
        
        cursor.close()
        connection.close()
        
        return animal_list
        
    except Exception as e:
        print(f"获取动物列表时出错: {e}")
        return []


def get_location_list():
    """
    获取所有地点列表
    
    Returns:
        list: 地点列表
    """
    try:
        # 连接SQLite数据库
        db_path = get_db_path()
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        table_name = get_table_name()
        sql = f"""
        SELECT DISTINCT location
        FROM {table_name}
        WHERE location IS NOT NULL AND location != ''
        ORDER BY location
        """
        
        cursor.execute(sql)
        results = cursor.fetchall()
        
        # 处理结果
        location_list = [row[0] for row in results]
        
        cursor.close()
        connection.close()
        
        return location_list
        
    except Exception as e:
        print(f"获取地点列表时出错: {e}")
        return []

# ==================== 地图数据和位置详情功能 ====================

def get_map_data(animal_type=None, start_date=None, end_date=None):
    """
    获取地图数据 - 动物分布监测点（基于经纬度坐标）
    
    Args:
        animal_type (str, optional): 动物种类筛选
        start_date (str, optional): 开始日期 (YYYY-MM-DD)
        end_date (str, optional): 结束日期 (YYYY-MM-DD)
    
    Returns:
        list: 包含地理位置和动物数量的数据列表
    """
    try:
        # 连接SQLite数据库
        db_path = get_db_path()
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        # 构建SQL查询 - 直接使用经纬度坐标
        table_name = get_table_name()
        base_sql = f"""
        SELECT 
            longitude,
            latitude,
            location,
            SUM(count) as count,
            GROUP_CONCAT(DISTINCT animal) as animal_types
        FROM {table_name}
        WHERE longitude IS NOT NULL 
        AND latitude IS NOT NULL 
        AND longitude != '' 
        AND latitude != ''
        """
        
        params = []
        
        # 添加筛选条件
        if animal_type and animal_type != 'all':
            base_sql += " AND animal = ?"
            params.append(animal_type)
            
        # 使用date字段进行日期筛选
        # 注意：数据库中date字段格式为YYYYMMDD，前端传递的是YYYY-MM-DD
        if start_date:
            # 将YYYY-MM-DD格式转换为YYYYMMDD格式
            start_date_formatted = start_date.replace('-', '')
            base_sql += " AND date >= ?"
            params.append(start_date_formatted)
            
        if end_date:
            # 将YYYY-MM-DD格式转换为YYYYMMDD格式
            end_date_formatted = end_date.replace('-', '')
            base_sql += " AND date <= ?"
            params.append(end_date_formatted)
        
        base_sql += " GROUP BY longitude, latitude, location ORDER BY count DESC"
        
        # 执行查询
        cursor.execute(base_sql, params)
        results = cursor.fetchall()
        
        # 处理结果
        map_data = []
        for row in results:
            longitude, latitude, location, count, animal_types = row
            try:
                # 处理带有方向前缀的经纬度数据
                # 经度: E/W前缀，纬度: N/S前缀
                lng_str = str(longitude).strip()
                lat_str = str(latitude).strip()
                
                # 解析经度
                if lng_str.startswith('E'):
                    lng = float(lng_str[1:])  # 东经为正
                elif lng_str.startswith('W'):
                    lng = -float(lng_str[1:])  # 西经为负
                else:
                    lng = float(lng_str)  # 直接数字
                
                # 解析纬度
                if lat_str.startswith('N'):
                    lat = float(lat_str[1:])  # 北纬为正
                elif lat_str.startswith('S'):
                    lat = -float(lat_str[1:])  # 南纬为负
                else:
                    lat = float(lat_str)  # 直接数字
                
                map_data.append({
                    'name': location or f"位置({lng:.4f},{lat:.4f})",
                    'value': count,
                    'animal_types': animal_types.split(',') if animal_types else [],
                    'coord': [lng, lat]  # 直接使用数据库中的经纬度
                })
            except (ValueError, TypeError) as e:
                # 跳过无效的坐标数据
                print(f"坐标转换失败: {e}, 原始数据: 经度='{longitude}', 纬度='{latitude}'")
                continue
        
        cursor.close()
        connection.close()
        
        return map_data
        
    except Exception as e:
        print(f"获取地图数据时出错: {e}")
        return []


def get_location_detail(longitude=None, latitude=None, location=None, start_date=None, end_date=None, limit=100):
    """
    获取指定坐标或地点的详细信息，包括最新图片
    
    Args:
        longitude (float, optional): 经度坐标
        latitude (float, optional): 纬度坐标  
        location (str, optional): 地点名称（备用）
        start_date (str, optional): 开始日期 (YYYY-MM-DD)
        end_date (str, optional): 结束日期 (YYYY-MM-DD)
        limit (int): 返回记录数量限制
    
    Returns:
        dict: 包含详情列表和最新媒体信息的字典
    """
    try:
        # 连接SQLite数据库
        db_path = get_db_path()
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        table_name = get_table_name()
        
        # 调试：查看数据库中的经纬度格式
        debug_sql = f"SELECT longitude, latitude, location FROM {table_name} LIMIT 5"
        cursor.execute(debug_sql)
        debug_results = cursor.fetchall()
        print(f"🔍 数据库中的经纬度格式示例: {debug_results}")
        
        # 构建基础SQL查询 - 获取最新的图片/视频和描述信息
        base_sql = f"""
        SELECT 
            animal,
            caption,
            time,
            location,
            longitude,
            latitude,
            image_id,
            count,
            date,
            path,
            type
        FROM {table_name}
        WHERE 1=1
        """
        
        params = []
        
        # 添加位置筛选条件
        if longitude is not None and latitude is not None:
            # 使用模糊匹配，允许小数点后2位的误差
            base_sql += " AND ABS(CAST(REPLACE(REPLACE(longitude, 'E', ''), 'W', '') AS DECIMAL(10,6)) - ?) < 0.01"
            base_sql += " AND ABS(CAST(REPLACE(REPLACE(latitude, 'N', ''), 'S', '') AS DECIMAL(10,6)) - ?) < 0.01"
            params.extend([longitude, latitude])
        elif location:
            base_sql += " AND location LIKE ?"
            params.append(f"%{location}%")
        else:
            return []
        
        # 添加时间段筛选条件
        if start_date:
            # 将YYYY-MM-DD格式转换为YYYYMMDD格式
            start_date_formatted = start_date.replace('-', '')
            base_sql += " AND date >= ?"
            params.append(start_date_formatted)
            
        if end_date:
            # 将YYYY-MM-DD格式转换为YYYYMMDD格式
            end_date_formatted = end_date.replace('-', '')
            base_sql += " AND date <= ?"
            params.append(end_date_formatted)
        
        # 按日期和时间排序，获取最新的记录
        base_sql += " ORDER BY date DESC, time DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(base_sql, params)
        results = cursor.fetchall()
        
        # 处理结果 - 按动物类型分组，获取每种动物的最新图片和描述
        animal_latest_data = {} # 一条记录用字典保存
        detail_data = []        # 所有记录用列表保存
        
        for row in results:
            animal, caption, time, location, lng, lat, image_id, count, date, path, media_type = row
            
            # 为每种动物保存最新的媒体文件和描述信息（因为返回的result是按照时间日期降序排列的，所以第一个记录就是最新的）
            if animal not in animal_latest_data:
                animal_latest_data[animal] = {
                    'latest_media': path if path else None,
                    'latest_media_type': media_type if media_type else 'image',  # 默认为图片类型
                    'latest_caption': caption,
                    'latest_time': str(time),
                    'latest_date': str(date)
                }
            
            detail_data.append({
                'animal_type': animal,
                'caption': caption,
                'time': str(time),
                'date': str(date),
                'location': location,
                'longitude': lng,
                'latitude': lat,
                'coordinates': f"({lng}, {lat})" if lng and lat else None,
                'media_path': path if path else None,
                'media_type': media_type if media_type else 'image',  # 默认为图片类型
                'count': count
            })
        
        cursor.close()
        connection.close()
        
        # 将最新图片信息添加到返回数据中
        return {
            'details': detail_data,
            'latest_by_animal': animal_latest_data
        }
        
    except Exception as e:
        print(f"获取地点详情时出错: {e}")
        return []

# ==================== 测试和调试功能 ====================

def main():
    """
    主函数 - 用于调试和测试echarts_map_data_functions.py中的所有函数
    
    测试内容：
    1. 测试动物列表和地点列表获取
    2. 测试地图数据获取
    3. 测试位置详情获取
    4. 验证数据格式和内容的正确性
    """
    print("🗺️ 开始调试 ECharts地图数据功能模块")
    print("=" * 60)
    
    # 第一部分：测试基础列表功能
    print("\n=== 📋 测试基础列表功能 ===")
    
    try:
        # 测试动物列表
        print("1️⃣ 获取动物列表...")
        animals = get_animal_list()
        print(f"✅ 成功获取 {len(animals)} 种动物")
        if animals:
            print(f"   动物种类: {animals}")
        
        # 测试地点列表
        print("\n2️⃣ 获取地点列表...")
        locations = get_location_list()
        print(f"✅ 成功获取 {len(locations)} 个地点")
        if locations:
            print(f"   地点列表: {locations}")
            
    except Exception as e:
        print(f"❌ 基础列表功能测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 第二部分：测试地图数据功能
    print("\n=== 📍 测试地图数据功能 ===")
    
    try:
        # 测试获取所有地图数据
        print("3️⃣ 获取所有地图数据...")
        all_map_data = get_map_data()
        print(f"✅ 成功获取 {len(all_map_data)} 个监测点")
        
        if all_map_data:
            # 显示前3个数据点的详细信息
            print("\n📊 前3个监测点详情:")
            for i, point in enumerate(all_map_data[:3]):
                print(f"  {i+1}. {point['name']}")
                print(f"     坐标: {point['coord']}")
                print(f"     监测数量: {point['value']}")
                print(f"     动物类型: {point['animal_types']}")
                print()
            
            # 测试按动物类型筛选
            print("4️⃣ 测试动物类型筛选...")
            first_animal_types = all_map_data[0]['animal_types']
            if first_animal_types:
                test_animal = first_animal_types[0]
                filtered_data = get_map_data(animal_type=test_animal)
                print(f"✅ 筛选动物类型 '{test_animal}': {len(filtered_data)} 个监测点")
            else:
                print("⚠️ 未找到可用的动物类型进行测试")
        
    except Exception as e:
        print(f"❌ 地图数据功能测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 第三部分：测试位置详情功能
    print("\n=== 🔍 测试位置详情功能 ===")
    
    try:
        if all_map_data:
            # 使用第一个监测点的坐标进行测试
            test_point = all_map_data[0]
            test_lng, test_lat = test_point['coord']
            test_location = test_point['name']
            
            print(f"5️⃣ 测试位置详情获取...")
            print(f"   测试坐标: ({test_lng}, {test_lat})")
            print(f"   测试地点: {test_location}")
            
            # 按坐标查询
            detail_data = get_location_detail(longitude=test_lng, latitude=test_lat)
            
            if detail_data and isinstance(detail_data, dict):
                details = detail_data.get('details', [])
                latest_by_animal = detail_data.get('latest_by_animal', {})
                
                print(f"✅ 获取详情记录: {len(details)} 条")
                print(f"✅ 动物类型数量: {len(latest_by_animal)} 种")
                
                # 显示最新媒体信息
                if latest_by_animal:
                    print("\n🖼️ 最新媒体信息:")
                    for animal, info in latest_by_animal.items():
                        print(f"   {animal}:")
                        print(f"     最新日期: {info.get('latest_date')}")
                        print(f"     最新时间: {info.get('latest_time')}")
                        print(f"     媒体类型: {info.get('latest_media_type', '未知')}")
                        print(f"     描述: {info.get('latest_caption', '无')[:50]}...")
            else:
                print("⚠️ 未获取到详情数据")
        
    except Exception as e:
        print(f"❌ 位置详情功能测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 总结
    print("\n" + "=" * 60)
    print("🎯 ECharts地图数据功能模块测试完成!")
    print("💡 所有功能已合并到一个文件中，便于维护和使用")
    print("📝 建议在生产环境中移除调试输出语句")

if __name__ == '__main__':
    """
    脚本直接运行时的入口点
    
    使用方法：
    1. 确保数据库连接配置正确 (db_config.py)
    2. 在命令行中运行: python echarts_map_data_functions.py
    3. 查看所有功能的测试结果
    """
    main()
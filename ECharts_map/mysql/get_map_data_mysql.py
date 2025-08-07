# get_map_data_mysql.py
import pymysql
from db_config import get_db_config, get_table_name

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
        # 连接数据库
        connection = pymysql.connect(**get_db_config())
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
            base_sql += " AND animal = %s"
            params.append(animal_type)
            
        # 使用date字段进行日期筛选
        # 注意：数据库中date字段格式为YYYYMMDD，前端传递的是YYYY-MM-DD
        if start_date:
            # 将YYYY-MM-DD格式转换为YYYYMMDD格式
            start_date_formatted = start_date.replace('-', '')
            base_sql += " AND date >= %s"
            params.append(start_date_formatted)
            
        if end_date:
            # 将YYYY-MM-DD格式转换为YYYYMMDD格式
            end_date_formatted = end_date.replace('-', '')
            base_sql += " AND date <= %s"
            params.append(end_date_formatted)
        
        base_sql += " GROUP BY longitude, latitude, location ORDER BY count DESC"
        
        # 可选：获取数据库中的日期范围（用于调试）
        # date_range_sql = f"SELECT MIN(date) as min_date, MAX(date) as max_date, COUNT(*) as total FROM {table_name}"
        # cursor.execute(date_range_sql)
        # date_range = cursor.fetchone()
        # print(f"📅 数据库日期范围: {date_range[0]} 到 {date_range[1]}, 总记录数: {date_range[2]}")
        
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
        list: 包含图片和详细信息的数据列表
    """
    try:
        # 连接数据库
        connection = pymysql.connect(**get_db_config())
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
            base_sql += " AND ABS(CAST(REPLACE(REPLACE(longitude, 'E', ''), 'W', '') AS DECIMAL(10,6)) - %s) < 0.01"
            base_sql += " AND ABS(CAST(REPLACE(REPLACE(latitude, 'N', ''), 'S', '') AS DECIMAL(10,6)) - %s) < 0.01"
            params.extend([longitude, latitude])
        elif location:
            base_sql += " AND location LIKE %s"
            params.append(f"%{location}%")
        else:
            return []
        
        # 添加时间段筛选条件
        if start_date:
            # 将YYYY-MM-DD格式转换为YYYYMMDD格式
            start_date_formatted = start_date.replace('-', '')
            base_sql += " AND date >= %s"
            params.append(start_date_formatted)
            
        if end_date:
            # 将YYYY-MM-DD格式转换为YYYYMMDD格式
            end_date_formatted = end_date.replace('-', '')
            base_sql += " AND date <= %s"
            params.append(end_date_formatted)
        
        # 按日期和时间排序，获取最新的记录
        base_sql += " ORDER BY date DESC, time DESC LIMIT %s"
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


def main():
    """
    主函数 - 用于调试和测试get_map_data.py中的函数
    
    测试内容：
    1. 测试get_map_data函数 - 获取地图数据
    2. 测试get_location_detail函数 - 获取位置详情
    3. 验证数据格式和内容的正确性
    4. 输出调试信息和统计结果
    """
    print("🗺️ 开始调试 get_map_data.py 模块")
    print("=" * 60)
    
    # # 第一部分：测试get_map_data函数
    # print("\n=== 📍 测试 get_map_data 函数 ===")
    
    # try:
    #     # 1. 测试获取所有地图数据
    #     print("1️⃣ 获取所有地图数据...")
    #     all_map_data = get_map_data()
    #     print(f"✅ 成功获取 {len(all_map_data)} 个监测点")
        
    #     if all_map_data:
    #         # 显示前3个数据点的详细信息
    #         print("\n📊 前3个监测点详情:")
    #         for i, point in enumerate(all_map_data[:3]):
    #             print(f"  {i+1}. {point['name']}")
    #             print(f"     坐标: {point['coord']}")
    #             print(f"     监测数量: {point['value']}")
    #             print(f"     动物类型: {point['animal_types']}")
    #             print()
        
    #     # 2. 测试按动物类型筛选
    #     print("2️⃣ 测试动物类型筛选...")
    #     if all_map_data:
    #         # 获取第一个动物类型进行测试
    #         first_animal_types = all_map_data[0]['animal_types']
    #         if first_animal_types:
    #             test_animal = first_animal_types[0]
    #             filtered_data = get_map_data(animal_type=test_animal)
    #             print(f"✅ 筛选动物类型 '{test_animal}': {len(filtered_data)} 个监测点")
    #         else:
    #             print("⚠️ 未找到可用的动物类型进行测试")
        
    #     # 3. 测试日期筛选
    #     print("3️⃣ 测试日期筛选...")
    #     date_filtered_data = get_map_data(start_date='2024-01-01', end_date='2024-12-31')
    #     print(f"✅ 2024年数据: {len(date_filtered_data)} 个监测点")
        
    # except Exception as e:
    #     print(f"❌ get_map_data 测试失败: {e}")
    #     import traceback
    #     traceback.print_exc()
    
    # 第二部分：测试get_location_detail函数
    print("\n=== 🔍 测试 get_location_detail 函数 ===")
    
    try:
        print("1️⃣ 获取所有地图数据...")
        all_map_data = get_map_data()
        print(f"✅ 成功获取 {len(all_map_data)} 个监测点")
        
        if all_map_data:
            # 使用第二个监测点的坐标进行测试
            test_point = all_map_data[1]  # 成都
            test_lng, test_lat = test_point['coord']
            test_location = test_point['name']
            
            print(f"4️⃣ 测试位置详情获取...")
            print(f"   测试坐标: ({test_lng}, {test_lat})")
            print(f"   测试地点: {test_location}")
            
            # 按坐标查询
            detail_data = get_location_detail(longitude=test_lng, latitude=test_lat)
            
            if detail_data and isinstance(detail_data, dict):
                details = detail_data.get('details', [])
                latest_by_animal = detail_data.get('latest_by_animal', {})
            # 1. 从 detail_data 字典中查找键名为 'details' 的值
            # 2. 如果找到了，返回对应的值
            # 3. 如果没找到，返回默认值 [] （空列表）
                
                print(f"✅ 获取详情记录: {len(details)} 条")
                print(f"✅ 动物类型数量: {len(latest_by_animal)} 种")
                
                # 显示详情数据统计
                if details:  # 字典
                    print("\n📋 详情数据统计:")
                    animal_counts = {}
                    for detail in details:
                        animal = detail.get('animal_type')
                        count = detail.get('count', 1)
                        if animal:
                            animal_counts[animal] = animal_counts.get(animal, 0) + count
                    
                    for animal, count in animal_counts.items():
                        print(f"   {animal}: {count} 只")
                    
                    total_count = sum(animal_counts.values())
                    print(f"   总计: {total_count} 只")
                
                # 显示最新媒体信息
                if latest_by_animal:
                    print("\n🖼️ 最新媒体信息:")
                    for animal, info in latest_by_animal.items():
                        print(f"   {animal}:")
                        print(f"     最新日期: {info.get('latest_date')}")
                        print(f"     最新时间: {info.get('latest_time')}")
                        print(f"     媒体类型: {info.get('latest_media_type', '未知')}")
                        print(f"     媒体路径: {info.get('latest_media', '无')}")
                        print(f"     描述: {info.get('latest_caption', '无')[:50]}...")
            else:
                print("⚠️ 未获取到详情数据")
            
            # 5. 测试按地点名称查询
            print(f"\n5️⃣ 测试按地点名称查询...")
            location_data = get_location_detail(location=test_location)
            if location_data and isinstance(location_data, dict):
                location_details = location_data.get('details', [])
                print(f"✅ 按地点名称查询: {len(location_details)} 条记录")
            else:
                print("⚠️ 按地点名称查询无结果")
                
        else:
            print("❌ 无法进行详情测试，因为没有可用的地图数据")
            
    except Exception as e:
        print(f"❌ get_location_detail 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 第三部分：数据一致性验证
    print("\n=== ⚖️ 数据一致性验证 ===")
    
    try:
        if all_map_data:
            print("6️⃣ 验证地图数据与详情数据的一致性...")
            
            # 随机选择几个点进行验证
            test_points = all_map_data[:min(3, len(all_map_data))]
            consistent_count = 0
            
            for i, point in enumerate(test_points):
                lng, lat = point['coord']
                map_value = point['value']
                location_name = point['name']
                
                print(f"\n   验证点 {i+1}: {location_name}")
                print(f"   地图显示数量: {map_value}")
                
                detail_data = get_location_detail(longitude=lng, latitude=lat)
                if detail_data and isinstance(detail_data, dict):
                    details = detail_data.get('details', [])
                    detail_total = sum(detail.get('count', 1) for detail in details)
                    
                    print(f"   详情统计数量: {detail_total}")
                    
                    if map_value == detail_total:
                        print(f"   ✅ 数据一致")
                        consistent_count += 1
                    else:
                        print(f"   ❌ 数据不一致 (差值: {abs(map_value - detail_total)})")
                else:
                    print(f"   ⚠️ 无法获取详情数据")
            
            print(f"\n📊 一致性验证结果: {consistent_count}/{len(test_points)} 个点数据一致")
            print(f"📈 一致性比例: {consistent_count/len(test_points)*100:.1f}%")
        
    except Exception as e:
        print(f"❌ 数据一致性验证失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 总结
    print("\n" + "=" * 60)
    print("🎯 调试测试完成!")
    print("💡 如需测试特定功能，可以修改main函数中的测试参数")
    print("📝 建议在生产环境中移除调试输出语句")


if __name__ == '__main__':
    """
    脚本直接运行时的入口点
    
    使用方法：
    1. 确保数据库连接配置正确 (db_config.py)
    2. 在命令行中运行: python get_map_data.py
    3. 查看函数测试结果和数据验证报告
    """
    main()
# get_map_data.py
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
        
        # 构建基础SQL查询
        base_sql = f"""
        SELECT 
            animal,
            caption,
            time,
            location,
            longitude,
            latitude,
            image_id,
            count
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
        
        base_sql += " ORDER BY time DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(base_sql, params)
        
        results = cursor.fetchall()
        
        # 处理结果
        detail_data = []
        for row in results:
            animal, caption, time, location, lng, lat, image_id, count = row
            detail_data.append({
                'animal_type': animal,
                'caption': caption,
                'time': str(time),
                'location': location,
                'longitude': lng,
                'latitude': lat,
                'coordinates': f"({lng}, {lat})" if lng and lat else None,
                'image_path': f'/static/images/{image_id}.jpg' if image_id else None,
                'count': count
            })
        
        cursor.close()
        connection.close()
        
        return detail_data
        
    except Exception as e:
        print(f"获取地点详情时出错: {e}")
        return []
"""
MySQL数据获取模块 - 合并版本
包含所有MySQL数据库相关的数据获取函数

包含的函数：
1. get_animal_list() - 获取动物种类列表
2. get_realtime_data() - 获取实时动物统计数据
3. get_location_data() - 获取地理位置统计数据
4. get_time_series_data() - 获取时间序列数据
5. get_activity_data() - 获取动物活动时间分布数据
"""

import pymysql
from db_config_mysql import get_db_config


def get_animal_list():
    """从image_info数据库获取所有动物种类列表"""
    try:
        db_config = get_db_config()
        connection = pymysql.connect(**db_config)
        
        with connection.cursor() as cursor:
            # 查询所有不同的动物种类
            # 从 image_info 表中获取所有不重复、非空的 animal 值，并按字母顺序排列。
            sql = "SELECT DISTINCT animal FROM image_info WHERE animal IS NOT NULL AND animal != '' ORDER BY animal;"
            cursor.execute(sql)
            result = cursor.fetchall()
            
            # 转换为列表
            animals = [row[0] for row in result]
            
            return {'status': 'success', 'data': animals}
            
    except pymysql.Error as e:
        return {"status": "error", "message": f"数据库错误: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"系统错误: {str(e)}"}
    finally:
        if 'connection' in locals():
            connection.close()


def get_realtime_data(days_filter=None):
    """从image_info数据库获取图像识别统计数据（支持时间筛选）"""
    try:
        db_config = get_db_config()
        connection = pymysql.connect(**db_config)
        
        with connection.cursor() as cursor:
            # 构建SQL查询，支持时间筛选
            if days_filter:
                sql = """
                SELECT animal, SUM(count) as total_count 
                FROM image_info 
                WHERE date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
                GROUP BY animal 
                ORDER BY total_count DESC 
                LIMIT 10;
                """
                cursor.execute(sql, (days_filter,))
                # WHERE命令：
                # 只保留最近 %s 天（从当前日期 CURDATE() 向前推 %s 天）及以后的记录
                # DATE_SUB(CURDATE(), INTERVAL %s DAY)：计算出 "今天减去 %s 天" 的日期
                # date >= …：只选取该日期及以后的行
            else:
                # 查询动物识别统计数据，使用SUM(count)统计每种动物的总数量
                sql = """
                SELECT animal, SUM(count) as total_count 
                FROM image_info 
                GROUP BY animal 
                ORDER BY total_count DESC 
                LIMIT 10;
                """
                cursor.execute(sql)
            
            result = cursor.fetchall()
            
            # 转换为字典列表
            data = []
            for row in result:
                data.append({
                    'animal': row[0],
                    'count': row[1]
                })
            # print("get_realtime_data:", data)
            
            return {'status': 'success', 'data': data}
            
    except pymysql.Error as e:
        return {"status": "error", "message": f"数据库错误: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"系统错误: {str(e)}"}
    finally:
        if 'connection' in locals():
            connection.close()


def get_location_data(animal_filter=None):
    """从image_info数据库获取地理位置统计数据
    
    Args:
        animal_filter (str, optional): 动物种类筛选条件，如果为None则显示所有动物
    """
    try:
        db_config = get_db_config()
        connection = pymysql.connect(**db_config)
        
        with connection.cursor() as cursor:
            # 构建SQL查询，根据是否有动物筛选条件
            if animal_filter and animal_filter != 'all':
                sql = """
                SELECT location, SUM(count) as total_count 
                FROM image_info 
                WHERE animal = %s 
                GROUP BY location 
                ORDER BY total_count DESC 
                LIMIT 10;
                """
                cursor.execute(sql, (animal_filter,))
            else:
                sql = """
                SELECT location, SUM(count) as total_count 
                FROM image_info 
                GROUP BY location 
                ORDER BY total_count DESC 
                LIMIT 10;
                """
                cursor.execute(sql)
            result = cursor.fetchall()
            
            # 转换为字典列表
            data = []
            for row in result:
                data.append({
                    'location': row[0],
                    'count': row[1]
                })
            # print("get_location_data:", data)
            
            return {'status': 'success', 'data': data}
            
    except pymysql.Error as e:
        return {"status": "error", "message": f"数据库错误: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"系统错误: {str(e)}"}
    finally:
        if 'connection' in locals():
            connection.close()


def get_time_series_data(animal_filter=None):
    """从image_info数据库获取时间序列数据
    
    Args:
        animal_filter (str, optional): 动物种类筛选条件，如果为None则显示所有动物
    """
    try:
        db_config = get_db_config()
        connection = pymysql.connect(**db_config)
        
        with connection.cursor() as cursor:
            # 构建SQL查询，根据是否有动物筛选条件
            if animal_filter and animal_filter != 'all':
                sql = """
                SELECT date, SUM(count) as total_count, AVG(confidence) as avg_confidence, AVG(percentage) as avg_percentage 
                FROM image_info 
                WHERE date IS NOT NULL AND date != '' AND animal = %s
                GROUP BY date 
                ORDER BY date DESC 
                LIMIT 20
                """
                cursor.execute(sql, (animal_filter,))
            # 1. SELECT 子句：要返回的列
            #   date：原始的日期字段，用来区分不同天的数据。
            #   SUM(count) AS total_count：对这一日期组内的 count 列做求和，把结果命名为 total_count，表示当天所有记录里"count"字段的累积值。
            #   AVG(confidence) AS avg_confidence：计算当天所有记录 confidence 字段的算术平均值，命名为 avg_confidence。
            #   AVG(percentage) AS avg_percentage：计算当天所有记录 percentage 字段的平均值，命名为 avg_percentage。
            # 2. FROM 子句：数据来源于表image_info
            # 3. WHERE 子句：过滤条件
            #   date IS NOT NULL AND date != ''：去掉日期为空或空字符串的记录，确保分组时日期有效。
            #   AND animal = %s：只统计 animal 列等于调用时传入参数（animal_filter）的那种动物。
            # 4. GROUP BY 子句：按日期分组
            #   GROUP BY date 会将所有同一天的记录聚到一起，分别计算每组的 SUM(count)、AVG(confidence)、AVG(percentage)。
            # 5. ORDER BY 子句：排序
            #   ORDER BY date DESC 按日期倒序排列，把最新的日期排在最前面。
            # 6. LIMIT 子句：数量限制
            #   LIMIT 20 只取前 20 条结果，也就是最近的 20 天的统计数据。
            else:
                sql = """
                SELECT date, SUM(count) as total_count, AVG(confidence) as avg_confidence, AVG(percentage) as avg_percentage 
                FROM image_info 
                WHERE date IS NOT NULL AND date != '' 
                GROUP BY date 
                ORDER BY date DESC 
                LIMIT 20
                """
                cursor.execute(sql)
            result = cursor.fetchall()
            
            # 转换为字典列表
            data = []
            for row in result:
                data.append({
                    'date': row[0],
                    'count': row[1],
                    'confidence': round(float(row[2]) if row[2] else 0, 2),
                    'percentage': round(float(row[3]) if row[3] else 0, 2)
                })
            
            # 反转数据，使时间顺序正确
            data.reverse()
            
            return {'status': 'success', 'data': data}
            
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
    finally:
        if 'connection' in locals():
            connection.close()


def get_activity_data(animal_filter=None):
    """从image_info数据库获取动物活动时间分布数据"""
    try:
        db_config = get_db_config()
        connection = pymysql.connect(**db_config)
        
        with connection.cursor() as cursor:
            # 构建SQL查询，按小时统计动物活动
            # 时间格式是 HH:MM，使用TIME函数解析
            if animal_filter and animal_filter != 'all':
                sql = """
                SELECT 
                    HOUR(TIME(time)) as hour,
                    SUM(count) as total_count
                FROM image_info 
                WHERE animal = %s AND time IS NOT NULL AND time != ''
                GROUP BY HOUR(TIME(time))
                ORDER BY hour;
                """
                cursor.execute(sql, (animal_filter,))
            else:
                sql = """
                SELECT 
                    HOUR(TIME(time)) as hour,
                    SUM(count) as total_count
                FROM image_info 
                WHERE time IS NOT NULL AND time != ''
                GROUP BY HOUR(TIME(time))
                ORDER BY hour;
                """
                cursor.execute(sql)
            
            result = cursor.fetchall()
            
            # 初始化24小时的数据（0-23小时）
            hour_counts = {row[0]: row[1] for row in result}
            
            # 构建24小时的数据字典，键为小时数，值为计数
            activity_data = {}
            for hour in range(24):
                activity_data[hour] = hour_counts.get(hour, 0)
            
            return {'status': 'success', 'data': activity_data}
            
    except pymysql.Error as e:
        return {"status": "error", "message": f"数据库错误: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"系统错误: {str(e)}"}
    finally:
        if 'connection' in locals():
            connection.close()


# 为了方便使用，提供一个函数字典
MYSQL_FUNCTIONS = {
    'get_animal_list': get_animal_list,
    'get_realtime_data': get_realtime_data,
    'get_location_data': get_location_data,
    'get_time_series_data': get_time_series_data,
    'get_activity_data': get_activity_data
}


if __name__ == "__main__":
    """测试所有函数"""
    print("测试MySQL数据获取函数...")
    
    # 测试动物列表
    print("\n1. 测试动物列表:")
    result = get_animal_list()
    print(f"状态: {result['status']}")
    if result['status'] == 'success':
        print(f"动物数量: {len(result['data'])}")
        print(f"前5种动物: {result['data'][:5] if result['data'] else '无数据'}")
    
    # 测试实时数据
    print("\n2. 测试实时数据:")
    result = get_realtime_data()
    print(f"状态: {result['status']}")
    if result['status'] == 'success':
        print(f"数据条数: {len(result['data'])}")
    
    # 测试地理位置数据
    print("\n3. 测试地理位置数据:")
    result = get_location_data()
    print(f"状态: {result['status']}")
    if result['status'] == 'success':
        print(f"地点数量: {len(result['data'])}")
    
    # 测试时间序列数据
    print("\n4. 测试时间序列数据:")
    result = get_time_series_data()
    print(f"状态: {result['status']}")
    if result['status'] == 'success':
        print(f"时间点数量: {len(result['data'])}")
    
    # 测试活动数据
    print("\n5. 测试活动数据:")
    result = get_activity_data()
    print(f"状态: {result['status']}")
    if result['status'] == 'success':
        print(f"24小时数据完整性: {len(result['data']) == 24}")
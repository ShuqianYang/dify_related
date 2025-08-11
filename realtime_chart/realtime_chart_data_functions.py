"""
SQLite版本的实时图表数据获取函数集合
包含所有数据获取相关的函数：
- get_animal_list: 获取动物种类列表
- get_realtime_data: 获取实时统计数据
- get_location_data: 获取地理位置统计数据
- get_time_series_data: 获取时间序列数据
- get_activity_data: 获取动物活动时间分布数据
"""

import sqlite3
from datetime import datetime, timedelta
try:
    from realtime_chart.db_config import get_db_path, get_table_name
except ImportError:
    from db_config import get_db_path, get_table_name


def get_animal_list():
    """从image_info数据库获取所有动物种类列表"""
    try:
        db_path = get_db_path()
        table_name = get_table_name()
        connection = sqlite3.connect(db_path)
        
        cursor = connection.cursor()
        # 查询所有不同的动物种类
        # 从 image_info 表中获取所有不重复、非空的 animal 值，并按字母顺序排列。
        sql = f"SELECT DISTINCT animal FROM {table_name} WHERE animal IS NOT NULL AND animal != '' ORDER BY animal;"
        cursor.execute(sql)
        result = cursor.fetchall()
        
        # 转换为列表
        animals = [row[0] for row in result]
        
        return {'status': 'success', 'data': animals}
        
    except sqlite3.Error as e:
        return {"status": "error", "message": f"数据库错误: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"系统错误: {str(e)}"}
    finally:
        if 'connection' in locals():
            connection.close()


def get_realtime_data(days_filter=None):
    """从image_info数据库获取图像识别统计数据（支持时间筛选）"""
    try:
        db_path = get_db_path()
        table_name = get_table_name()
        connection = sqlite3.connect(db_path)
        
        cursor = connection.cursor()
        # 构建SQL查询，支持时间筛选
        if days_filter:
            # SQLite中计算日期差异的方法
            cutoff_date = (datetime.now() - timedelta(days=days_filter)).strftime('%Y%m%d')
            sql = f"""
            SELECT animal, SUM(count) as total_count 
            FROM {table_name} 
            WHERE date >= ?
            GROUP BY animal 
            ORDER BY total_count DESC 
            LIMIT 10;
            """
            cursor.execute(sql, (cutoff_date,))
            # WHERE命令：
            # 只保留最近 days_filter 天及以后的记录
            # 使用Python计算截止日期，然后与数据库中的date字段比较
        else:
            # 查询动物识别统计数据，使用SUM(count)统计每种动物的总数量
            sql = f"""
            SELECT animal, SUM(count) as total_count 
            FROM {table_name} 
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
        
    except sqlite3.Error as e:
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
        db_path = get_db_path()
        table_name = get_table_name()
        connection = sqlite3.connect(db_path)
        
        cursor = connection.cursor()
        # 构建SQL查询，根据是否有动物筛选条件
        if animal_filter and animal_filter != 'all':
            sql = f"""
            SELECT location, SUM(count) as total_count 
            FROM {table_name} 
            WHERE animal = ? 
            GROUP BY location 
            ORDER BY total_count DESC 
            LIMIT 10;
            """
            cursor.execute(sql, (animal_filter,))
        else:
            sql = f"""
            SELECT location, SUM(count) as total_count 
            FROM {table_name} 
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
        
    except sqlite3.Error as e:
        return {"status": "error", "message": f"数据库错误: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"系统错误: {str(e)}"}
    finally:
        if 'connection' in locals():
            connection.close()


def get_time_series_data(animal_filter=None):
    """从image_info数据库获取时间序列数据（按季度聚合）
    
    Args:
        animal_filter (str, optional): 动物种类筛选条件，如果为None则显示所有动物
    """
    try:
        db_path = get_db_path()
        table_name = get_table_name()
        connection = sqlite3.connect(db_path)
        
        cursor = connection.cursor()
        # 构建SQL查询，按季度聚合数据
        if animal_filter and animal_filter != 'all':
            sql = f"""
            SELECT 
                substr(date, 1, 4) as year,
                CASE 
                    WHEN substr(date, 5, 2) IN ('01', '02', '03') THEN '1季度'
                    WHEN substr(date, 5, 2) IN ('04', '05', '06') THEN '2季度'
                    WHEN substr(date, 5, 2) IN ('07', '08', '09') THEN '3季度'
                    WHEN substr(date, 5, 2) IN ('10', '11', '12') THEN '4季度'
                    ELSE '未知'
                END as quarter,
                SUM(count) as total_count, 
                AVG(confidence) as avg_confidence, 
                AVG(percentage) as avg_percentage 
            FROM {table_name} 
            WHERE date IS NOT NULL AND date != '' AND animal = ?
            GROUP BY year, quarter
            ORDER BY year DESC, quarter DESC 
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
        #   AND animal = ?：只统计 animal 列等于调用时传入参数（animal_filter）的那种动物。
        # 4. GROUP BY 子句：按日期分组
        #   GROUP BY date 会将所有同一天的记录聚到一起，分别计算每组的 SUM(count)、AVG(confidence)、AVG(percentage)。
        # 5. ORDER BY 子句：排序
        #   ORDER BY date DESC 按日期倒序排列，把最新的日期排在最前面。
        # 6. LIMIT 子句：数量限制
        #   LIMIT 20 只取前 20 条结果，也就是最近的 20 天的统计数据。
        else:
            sql = f"""
            SELECT 
                substr(date, 1, 4) as year,
                CASE 
                    WHEN substr(date, 5, 2) IN ('01', '02', '03') THEN '1季度'
                    WHEN substr(date, 5, 2) IN ('04', '05', '06') THEN '2季度'
                    WHEN substr(date, 5, 2) IN ('07', '08', '09') THEN '3季度'
                    WHEN substr(date, 5, 2) IN ('10', '11', '12') THEN '4季度'
                    ELSE '未知'
                END as quarter,
                SUM(count) as total_count, 
                AVG(confidence) as avg_confidence, 
                AVG(percentage) as avg_percentage 
            FROM {table_name} 
            WHERE date IS NOT NULL AND date != '' 
            GROUP BY year, quarter
            ORDER BY year DESC, quarter DESC 
            LIMIT 20
            """
            cursor.execute(sql)
        result = cursor.fetchall()
        
        # 转换为字典列表，格式化为"2021年1季度"的形式
        data = []
        for row in result:
            quarter_label = f"{row[0]}年{row[1]}"
            data.append({
                'date': quarter_label,
                'count': row[2],
                'confidence': round(float(row[3]) if row[3] else 0, 2),
                'percentage': round(float(row[4]) if row[4] else 0, 2)
            })
        
        # 反转数据，使时间顺序正确（从早到晚）
        data.reverse()
        
        return {'status': 'success', 'data': data}
        
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
    finally:
        if 'connection' in locals():
            connection.close()


def get_behavior_list(animal_filter=None):
    """从image_info数据库获取行为列表"""
    try:
        db_path = get_db_path()
        table_name = get_table_name()
        connection = sqlite3.connect(db_path)
        
        cursor = connection.cursor()
        # 构建SQL查询，获取行为列表
        if animal_filter and animal_filter != 'all':
            sql = f"""
            SELECT DISTINCT behavior 
            FROM {table_name} 
            WHERE animal = ? AND behavior IS NOT NULL AND behavior != '' 
            ORDER BY behavior;
            """
            cursor.execute(sql, (animal_filter,))
        else:
            sql = f"""
            SELECT DISTINCT behavior 
            FROM {table_name} 
            WHERE behavior IS NOT NULL AND behavior != '' 
            ORDER BY behavior;
            """
            cursor.execute(sql)
        
        result = cursor.fetchall()
        
        # 转换为列表
        behaviors = [row[0] for row in result]
        
        return {'status': 'success', 'data': behaviors}
        
    except sqlite3.Error as e:
        return {"status": "error", "message": f"数据库错误: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"系统错误: {str(e)}"}
    finally:
        if 'connection' in locals():
            connection.close()


def get_activity_data(animal_filter=None, behavior_filter=None):
    """从image_info数据库获取动物活动时间分布数据（支持动物和行为筛选）"""
    try:
        db_path = get_db_path()
        table_name = get_table_name()
        connection = sqlite3.connect(db_path)
        
        cursor = connection.cursor()
        # 构建SQL查询，按小时统计动物活动
        # 时间格式是 HH:MM，使用SQLite的时间函数解析
        
        # 构建WHERE条件
        where_conditions = ["time IS NOT NULL AND time != ''"]
        params = []
        
        if animal_filter and animal_filter != 'all':
            where_conditions.append("animal = ?")
            params.append(animal_filter)
            
        if behavior_filter and behavior_filter != 'all':
            where_conditions.append("behavior = ?")
            params.append(behavior_filter)
        
        where_clause = " AND ".join(where_conditions)
        
        sql = f"""
        SELECT 
            CAST(strftime('%H', time) AS INTEGER) as hour,
            SUM(count) as total_count
        FROM {table_name} 
        WHERE {where_clause}
        GROUP BY CAST(strftime('%H', time) AS INTEGER)
        ORDER BY hour;
        """
        cursor.execute(sql, params)
        
        result = cursor.fetchall()
        
        # 初始化24小时的数据（0-23小时）
        hour_counts = {row[0]: row[1] for row in result}
        
        # 构建24小时的数据字典，键为小时数，值为计数
        activity_data = {}
        for hour in range(24):
            activity_data[hour] = hour_counts.get(hour, 0)
        
        return {'status': 'success', 'data': activity_data}
        
    except sqlite3.Error as e:
        return {"status": "error", "message": f"数据库错误: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"系统错误: {str(e)}"}
    finally:
        if 'connection' in locals():
            connection.close()


def main():
    """主函数 - 测试所有数据获取功能"""
    print("=" * 60)
    print("SQLite 数据获取函数测试")
    print("=" * 60)
    
    # 测试 1: 获取动物列表
    print("\n1. 测试 get_animal_list()")
    print("-" * 40)
    result = get_animal_list()
    if result['status'] == 'success':
        print(f"✓ 成功获取动物列表")
        print(f"  动物种类数量: {len(result['data'])}")
        print(f"  动物列表: {result['data']}")
    else:
        print(f"✗ 获取动物列表失败: {result['message']}")
    
    # 测试 2: 获取实时数据（无筛选）
    print("\n2. 测试 get_realtime_data() - 无时间筛选")
    print("-" * 40)
    result = get_realtime_data()
    if result['status'] == 'success':
        print(f"✓ 成功获取实时数据")
        print(f"  数据条数: {len(result['data'])}")
        for i, item in enumerate(result['data'][:3]):  # 显示前3条
            print(f"  {i+1}. {item['animal']}: {item['count']}只")
    else:
        print(f"✗ 获取实时数据失败: {result['message']}")
    
    # 测试 3: 获取实时数据（7天筛选）
    print("\n3. 测试 get_realtime_data(days_filter=7) - 7天筛选")
    print("-" * 40)
    result = get_realtime_data(days_filter=7)
    if result['status'] == 'success':
        print(f"✓ 成功获取7天内实时数据")
        print(f"  数据条数: {len(result['data'])}")
        for i, item in enumerate(result['data'][:3]):  # 显示前3条
            print(f"  {i+1}. {item['animal']}: {item['count']}只")
    else:
        print(f"✗ 获取7天内实时数据失败: {result['message']}")
    
    # 测试 4: 获取地理位置数据（无筛选）
    print("\n4. 测试 get_location_data() - 无动物筛选")
    print("-" * 40)
    result = get_location_data()
    if result['status'] == 'success':
        print(f"✓ 成功获取地理位置数据")
        print(f"  数据条数: {len(result['data'])}")
        for i, item in enumerate(result['data'][:3]):  # 显示前3条
            print(f"  {i+1}. {item['location']}: {item['count']}只")
    else:
        print(f"✗ 获取地理位置数据失败: {result['message']}")
    
    # 测试 5: 获取时间序列数据（无筛选）
    print("\n5. 测试 get_time_series_data() - 无动物筛选")
    print("-" * 40)
    result = get_time_series_data()
    if result['status'] == 'success':
        print(f"✓ 成功获取时间序列数据")
        print(f"  数据条数: {len(result['data'])}")
        for i, item in enumerate(result['data'][:3]):  # 显示前3条
            print(f"  {i+1}. {item['date']}: 数量={item['count']}, 置信度={item['confidence']}%, 百分比={item['percentage']}%")
    else:
        print(f"✗ 获取时间序列数据失败: {result['message']}")
    
    # 测试 6: 获取活动时间数据（无筛选）
    print("\n6. 测试 get_activity_data() - 无动物筛选")
    print("-" * 40)
    result = get_activity_data()
    if result['status'] == 'success':
        print(f"✓ 成功获取活动时间数据")
        print("  24小时活动分布（前8小时）:")
        for hour in range(8):
            print(f"    {hour:2d}时: {result['data'][hour]:3d}次")
        # 统计总活动次数
        total_activity = sum(result['data'].values())
        print(f"  全天总活动次数: {total_activity}")
    else:
        print(f"✗ 获取活动时间数据失败: {result['message']}")
    
    # 获取第一个动物进行筛选测试
    animals_result = get_animal_list()
    if animals_result['status'] == 'success' and animals_result['data']:
        test_animal = animals_result['data'][0]
        
        print(f"\n7. 带动物筛选的测试 (测试动物: {test_animal})")
        print("-" * 40)
        
        # 测试地理位置数据（带动物筛选）
        print(f"7.1 get_location_data('{test_animal}')")
        result = get_location_data(test_animal)
        if result['status'] == 'success':
            print(f"  ✓ 成功获取 {test_animal} 的地理位置数据，数据条数: {len(result['data'])}")
            for i, item in enumerate(result['data'][:2]):  # 显示前2条
                print(f"    {i+1}. {item['location']}: {item['count']}次")
        else:
            print(f"  ✗ 获取 {test_animal} 地理位置数据失败: {result['message']}")
        
        # 测试时间序列数据（带动物筛选）
        print(f"7.2 get_time_series_data('{test_animal}')")
        result = get_time_series_data(test_animal)
        if result['status'] == 'success':
            print(f"  ✓ 成功获取 {test_animal} 的时间序列数据，数据条数: {len(result['data'])}")
            for i, item in enumerate(result['data'][:2]):  # 显示前2条
                print(f"    {i+1}. {item['date']}: {item['count']}次")
        else:
            print(f"  ✗ 获取 {test_animal} 时间序列数据失败: {result['message']}")
        
        # 测试活动时间数据（带动物筛选）
        print(f"7.3 get_activity_data('{test_animal}')")
        result = get_activity_data(test_animal)
        if result['status'] == 'success':
            print(f"  ✓ 成功获取 {test_animal} 的活动时间数据")
            # 找出活动最频繁的时间段
            max_hour = max(result['data'], key=result['data'].get)
            max_count = result['data'][max_hour]
            print(f"    最活跃时间: {max_hour}时 ({max_count}次)")
            total_activity = sum(result['data'].values())
            print(f"    总活动次数: {total_activity}")
        else:
            print(f"  ✗ 获取 {test_animal} 活动时间数据失败: {result['message']}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
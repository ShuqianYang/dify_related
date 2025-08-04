import pymysql
from realtime_chart.db_config import get_db_config

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
            #   SUM(count) AS total_count：对这一日期组内的 count 列做求和，把结果命名为 total_count，表示当天所有记录里“count”字段的累积值。
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
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
                SELECT date, COUNT(*) as count, AVG(confidence) as avg_confidence, AVG(percentage) as avg_percentage 
                FROM image_info 
                WHERE date IS NOT NULL AND date != '' AND animal = %s
                GROUP BY date 
                ORDER BY date DESC 
                LIMIT 20
                """
                cursor.execute(sql, (animal_filter,))
            else:
                sql = """
                SELECT date, COUNT(*) as count, AVG(confidence) as avg_confidence, AVG(percentage) as avg_percentage 
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
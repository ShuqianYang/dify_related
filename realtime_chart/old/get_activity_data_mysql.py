import pymysql
from realtime_chart.db_config_mysql import get_db_config

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
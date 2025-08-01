import pymysql
from realtime_chart.db_config import get_db_config

def get_behavior_data():
    """从image_info数据库获取动物行为统计数据"""
    try:
        db_config = get_db_config()
        connection = pymysql.connect(**db_config)
        
        with connection.cursor() as cursor:
            # 查询动物行为统计数据
            sql = "SELECT behavior, COUNT(*) as count FROM image_info GROUP BY behavior ORDER BY count DESC LIMIT 10"
            cursor.execute(sql)
            result = cursor.fetchall()
            
            # 转换为字典列表
            data = []
            for row in result:
                data.append({
                    'behavior': row[0],
                    'count': row[1]
                })
            
            return {'status': 'success', 'data': data}
            
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
    finally:
        if 'connection' in locals():
            connection.close()

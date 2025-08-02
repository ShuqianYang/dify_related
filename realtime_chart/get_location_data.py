import pymysql
from realtime_chart.db_config import get_db_config

def get_location_data():
    """从image_info数据库获取地理位置统计数据"""
    try:
        db_config = get_db_config()
        connection = pymysql.connect(**db_config)
        
        with connection.cursor() as cursor:
            # 查询地理位置统计数据，从高到低排序
            sql = "SELECT location, COUNT(*) as count FROM image_info GROUP BY location ORDER BY count DESC LIMIT 10;"
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
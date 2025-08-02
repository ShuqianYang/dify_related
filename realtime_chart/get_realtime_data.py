import pymysql
from realtime_chart.db_config import get_db_config

def get_realtime_data():
    """从image_info数据库获取图像识别统计数据"""
    try:
        db_config = get_db_config()
        connection = pymysql.connect(**db_config)
        
        with connection.cursor() as cursor:
            # 查询动物识别统计数据，按照顺序从高到低排序
            sql = "SELECT animal, COUNT(*) as count FROM image_info GROUP BY animal ORDER BY count DESC LIMIT 10;"
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
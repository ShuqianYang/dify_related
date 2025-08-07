import pymysql
from realtime_chart.db_config_mysql import get_db_config

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
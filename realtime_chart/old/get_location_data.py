import sqlite3
from realtime_chart.db_config import get_db_path, get_table_name

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
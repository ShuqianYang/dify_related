import sqlite3
from realtime_chart.db_config import get_db_path, get_table_name

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
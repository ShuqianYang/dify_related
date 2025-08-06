import pymysql
from realtime_chart.db_config_mysql import get_db_config

def get_animal_list():
    """从image_info数据库获取所有动物种类列表"""
    try:
        db_config = get_db_config()
        connection = pymysql.connect(**db_config)
        
        with connection.cursor() as cursor:
            # 查询所有不同的动物种类
            # 从 image_info 表中获取所有不重复、非空的 animal 值，并按字母顺序排列。
            sql = "SELECT DISTINCT animal FROM image_info WHERE animal IS NOT NULL AND animal != '' ORDER BY animal;"
            cursor.execute(sql)
            result = cursor.fetchall()
            
            # 转换为列表
            animals = [row[0] for row in result]
            
            return {'status': 'success', 'data': animals}
            
    except pymysql.Error as e:
        return {"status": "error", "message": f"数据库错误: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"系统错误: {str(e)}"}
    finally:
        if 'connection' in locals():
            connection.close()
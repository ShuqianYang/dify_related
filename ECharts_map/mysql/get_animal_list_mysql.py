# get_animal_list_mysql.py
import pymysql
from db_config import get_db_config, get_table_name

def get_animal_list():
    """
    获取所有动物种类列表
    
    Returns:
        list: 动物种类列表
    """
    try:
        # 连接数据库
        connection = pymysql.connect(**get_db_config())
        cursor = connection.cursor()
        
        table_name = get_table_name()
        sql = f"""
        SELECT DISTINCT animal
        FROM {table_name}
        WHERE animal IS NOT NULL AND animal != ''
        ORDER BY animal
        """
        
        cursor.execute(sql)
        results = cursor.fetchall()
        
        # 处理结果
        animal_list = [row[0] for row in results]
        
        cursor.close()
        connection.close()
        
        return animal_list
        
    except Exception as e:
        print(f"获取动物列表时出错: {e}")
        return []

def get_location_list():
    """
    获取所有地点列表
    
    Returns:
        list: 地点列表
    """
    try:
        # 连接数据库
        connection = pymysql.connect(**get_db_config())
        cursor = connection.cursor()
        
        table_name = get_table_name()
        sql = f"""
        SELECT DISTINCT location
        FROM {table_name}
        WHERE location IS NOT NULL AND location != ''
        ORDER BY location
        """
        
        cursor.execute(sql)
        results = cursor.fetchall()
        
        # 处理结果
        location_list = [row[0] for row in results]
        
        cursor.close()
        connection.close()
        
        return location_list
        
    except Exception as e:
        print(f"获取地点列表时出错: {e}")
        return []
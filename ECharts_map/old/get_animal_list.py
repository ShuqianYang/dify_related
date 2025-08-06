# get_animal_list.py
import sqlite3
from db_config import get_db_path, get_table_name

def get_animal_list():
    """
    获取所有动物种类列表
    
    Returns:
        list: 动物种类列表
    """
    try:
        # 连接SQLite数据库
        db_path = get_db_path()
        connection = sqlite3.connect(db_path)
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
        # 连接SQLite数据库
        db_path = get_db_path()
        connection = sqlite3.connect(db_path)
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

def main():
    """
    测试函数
    """
    print("🐾 测试动物列表获取功能")
    print("=" * 40)
    
    # 测试获取动物列表
    print("1️⃣ 获取动物列表...")
    animals = get_animal_list()
    print(f"✅ 成功获取 {len(animals)} 种动物")
    if animals:
        print(f"   动物种类: {animals[:5]}{'...' if len(animals) > 5 else ''}")
    
    # 测试获取地点列表
    print("\n2️⃣ 获取地点列表...")
    locations = get_location_list()
    print(f"✅ 成功获取 {len(locations)} 个地点")
    if locations:
        print(f"   地点列表: {locations[:5]}{'...' if len(locations) > 5 else ''}")

if __name__ == "__main__":
    main()
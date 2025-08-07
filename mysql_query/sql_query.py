# sql_query.py - SQLite版本
import sqlite3
try:
    from .db_config import get_db_path
except ImportError:
    from db_config import get_db_path

def query_sql(sql: str) -> dict:
    """
    执行 SQL 语句（只允许 SELECT），无查询结果时返回空列表
    """
    if not sql.strip().lower().startswith(("select")):
        return {"status": "error", "message": "仅允许执行 SELECT 语句"}
    
    db_path = get_db_path()
    # print(f"数据库路径: {db_path}")
    
    try:
        connection = sqlite3.connect(db_path)
        connection.row_factory = sqlite3.Row  # 使结果可以通过列名访问
        cursor = connection.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()  # 获取查询结果
        # print(result) 
        # print(type(result))
        
        # 将结果转换为字典列表
        formatted_result = []
        if result:
            for row in result:
                formatted_result.append(dict(row))
                
        return {"status": "success", "data": formatted_result}
    except sqlite3.Error as e:
        return {"status": "error", "message": f"数据库错误: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"系统错误: {str(e)}"}
    finally:
        if 'connection' in locals() and connection:
            connection.close()

if __name__ == "__main__":
    # 测试 execute_sql 函数
    test_sql = "SELECT DISTINCT 保护级别 FROM protected_species;"

    result = query_sql(test_sql)
    print(result)

    
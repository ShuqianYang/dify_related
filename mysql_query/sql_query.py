# sql_query.py
import pymysql
# from db_config import get_db_config
from mysql_query.db_config import get_db_config

def query_sql(sql: str) -> dict:
    """
    执行 SQL 语句（只允许 SELECT）
    """
    if not sql.lower().startswith(("select")):
        return {"status": "error", "message": "仅允许执行 SELECT 语句"}
    
    config = get_db_config()
    print(config)
    
    try:
        connection = pymysql.connect(**config)
        with connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()  # 获取查询结果
            
            # 获取列名
            columns = [col[0] for col in cursor.description]
            
            # 将结果转换为字典列表
            # formatted_result = []
            for row in result:
                # formatted_result.append(dict(zip(columns, row)))
                formatted_result = dict(zip(columns, row))            
        return {"status": "success", "data": formatted_result}
    except pymysql.Error as e:
        return {"status": "error", "message": f"数据库错误: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"系统错误: {str(e)}"}
    finally:
        if 'connection' in locals() and connection:
            connection.close()

if __name__ == "__main__":
    # 测试 execute_sql 函数
    test_sql = "SELECT * FROM `国家重点保护野生动物名录` WHERE 中文名 = '驼鹿';"

    result = query_sql(test_sql)
    print(result)

    
# sql_insert.py
import pymysql
from mysql_insert.db_config import get_db_config


def execute_sql(sql: str) -> dict:
    """
    执行 SQL 语句（只允许 INSERT 或 UPDATE）
    """
    if not sql.lower().startswith(("insert", "update")):
        return {"status": "error", "message": "仅允许执行 INSERT 或 UPDATE 语句"}

    config = get_db_config()
    print(config)

    try:
        connection = pymysql.connect(**config)
        with connection.cursor() as cursor:
            cursor.execute(sql)
        connection.commit()  # 提交数据库事务，持久化修改结果
        return {"status": "success", "message": "SQL 执行成功"}
    except pymysql.Error as e: 
        # 捕获 pymysql 特有的错误（如连接失败、SQL 执行错误等）。如果数据库操作发生错误，代码会进入这个 except 块。
        return {"status": "error", "message": f"数据库错误: {e}"}
    except Exception as e:
        # 捕获所有非数据库错误的异常。比如数据库连接建立成功，但是程序本身出现了其他错误，如内存溢出、文件操作失败等。
        return {"status": "error", "message": f"系统错误: {str(e)}"}
    finally: 
        # 无论是否成功，都会执行finally操作：关闭数据库连接释放资源。
        if 'connection' in locals() and connection:
            # 检查 connection 是否存在且有效。如果 connection 被成功创建并且是有效的，就执行关闭操作。
            connection.close()

if __name__ == "__main__":
    # 测试 execute_sql 函数
    test_sql = "INSERT INTO image_info (object, count, behavior, status, percentage, confidence, caption, image_id, sensor_id, location, longitude, latitude, time, date, insert_time) VALUES ('动物', 1, '正在吃草', '健康，自然状态', 25, 95, '图中展示了一只驼鹿在吃草', '08997y8y', 'ihoioioijoi', '成都', '133.25', '35.5', '0325', '20050726', '0326');"

    result = execute_sql(test_sql)
    print(result)

# sql_operations.py
# 合并了 sql_generator.py 和 sql_insert.py 的功能
import json
import sqlite3

try:
    from .db_config import get_db_path
except ImportError:
    from db_config import get_db_path


def generate_sql(data: dict) -> dict:
    """
    将JSON数据转换为SQLite INSERT语句
    """
    try:
        table_name = "image_info"
        required_fields = ['object', 'animal', 'count', 'behavior', 'status', 'percentage', 'confidence', 'image_id', 'sensor_id', 'location', 'longitude', 'latitude', 'time', 'date', 'caption']
        optional_fields = ['type', 'path']

        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return {
                'status': 'error',
                'message': f"错误：缺少必填字段 - {', '.join(missing_fields)}"
            } 

        fields = []
        values = []

        all_fields = required_fields + optional_fields
        for field in all_fields:
            if field in data:
                fields.append(field)
                value = data[field]
                
                if value is None:
                    values.append("NULL")
                elif isinstance(value, str):
                    escaped_value = value.replace("'", "''")
                    values.append(f"'{escaped_value}'")
                elif isinstance(value, (int, float)):
                    values.append(str(value))
                else:
                    return {
                        'status': 'error',
                        'message': f"错误：字段 '{field}' 类型不支持 - {type(value)}"
                    }

        sql = f"INSERT INTO {table_name} ({', '.join(fields)}) VALUES ({', '.join(values)});"
        return {'status': 'success', 'message': sql}
    
    except json.JSONDecodeError:
        return {'status': 'error', 'message': "错误：无效的JSON格式"}
    except Exception as e:
        return {'status': 'error', 'message': f"错误：{str(e)}"}


def execute_sql(sql: str) -> dict:
    """
    执行 SQL 语句（只允许 INSERT 或 UPDATE）
    """
    if not sql.lower().startswith(("insert", "update")):
        return {"status": "error", "message": "仅允许执行 INSERT 或 UPDATE 语句"}

    db_path = get_db_path()
    # print(f"数据库路径: {db_path}")

    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()  # 提交数据库事务，持久化修改结果
        return {"status": "success", "message": "SQL 执行成功"}
    except sqlite3.Error as e: 
        # 捕获 sqlite3 特有的错误（如连接失败、SQL 执行错误等）。如果数据库操作发生错误，代码会进入这个 except 块。
        return {"status": "error", "message": f"数据库错误: {e}"}
    except Exception as e:
        # 捕获所有非数据库错误的异常。比如数据库连接建立成功，但是程序本身出现了其他错误，如内存溢出、文件操作失败等。
        return {"status": "error", "message": f"系统错误: {str(e)}"}
    finally: 
        # 无论是否成功，都会执行finally操作：关闭数据库连接释放资源。
        if 'connection' in locals() and connection:
            # 检查 connection 是否存在且有效。如果 connection 被成功创建并且是有效的，就执行关闭操作。
            connection.close()


def generate_and_execute_sql(data: dict) -> dict:
    """
    组合函数：生成SQL语句并执行
    """
    # 生成SQL语句
    sql_result = generate_sql(data)
    if sql_result['status'] == 'error':
        return sql_result
    
    sql_statement = sql_result['message']
    
    # 执行SQL语句
    execute_result = execute_sql(sql_statement)
    
    # 返回执行结果，同时包含生成的SQL语句信息
    if execute_result['status'] == 'success':
        return {
            'status': 'success',
            'message': execute_result['message'],
            'sql': sql_statement
        }
    else:
        return {
            'status': 'error',
            'message': execute_result['message'],
            'sql': sql_statement
        }


if __name__ == "__main__":
    # 测试数据
    test_data = {
        "object": "动物",
        "animal": "驼鹿",
        "count": 1,
        "behavior": "正在吃草",
        "status": "健康，自然状态",
        "percentage": 25,
        "confidence": 95,
        "caption": "图中展示了一只驼鹿在吃草",
        "image_id": "08997y8y",
        "sensor_id": "ihoioioijoi",
        "location": "成都",
        "longitude": "133.25",
        "latitude": "35.5",
        "time": "0325",
        "date": "20050726",
        "type": "image",
        "path": "/images/moose_001.jpg"
    }

    print("=== 测试 generate_sql 函数 ===")
    sql_result = generate_sql(test_data)
    print(sql_result)
    
    if sql_result['status'] == 'success':
        print("\n=== 测试 execute_sql 函数 ===")
        execute_result = execute_sql(sql_result['message'])
        print(execute_result)
    
    print("\n=== 测试 generate_and_execute_sql 组合函数 ===")
    combined_result = generate_and_execute_sql(test_data)
    print(combined_result)
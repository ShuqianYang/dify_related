from flask import Flask, request, jsonify
import json
import pymysql

app = Flask(__name__)

# 数据库配置
DB_HOST = "localhost"  # 172.24.224.1
DB_USER = "root"
DB_PASSWORD = "123456"
DB_NAME = "dify_test"
DB_PORT = 3306
DB_CHARSET = "utf8mb4"

def generate_sql(data: dict) -> dict:
    """
    将JSON数据转换为MySQL INSERT语句
    
    Args:
        json_data (dict): 字典格式数据
        
    Returns:
        dict: 包含结果状态和消息的字典
    """
    try:
        # # 解析JSON数据
        # data = json.loads(json_data)

        # 定义表结构
        table_name = "image_info"
        required_fields = ['object', 'count', 'behavior', 'status', 'percentage', 'confidence', 'caption', 'image_id', 'sensor_id', 'location', 'longitude', 'latitude', 'time', 'date', 'insert_time']
        optional_fields = ['animal']

        # 检查必填字段
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return {
                'status': 'error',
                'message': f"错误：缺少必填字段 - {', '.join(missing_fields)}"
            } 
        
        # 收集字段和值
        fields = []
        values = []

        # 处理所有字段
        all_fields = required_fields + optional_fields
        for field in all_fields:
            if field in data:
                fields.append(field)
                value = data[field]
                
                # 处理NULL值
                if value is None:
                    values.append("NULL")
                # 处理字符串类型
                elif isinstance(value, str):
                    # 转义字符串中的单引号
                    escaped_value = value.replace("'", "''")
                    values.append(f"'{escaped_value}'")
                # 处理数字类型
                elif isinstance(value, (int, float)):
                    values.append(str(value))
                else:
                    return {
                        'status': 'error',
                        'message': f"错误：字段 '{field}' 类型不支持 - {type(value)}"
                    }
        
        # 构建SQL语句
        sql = f"INSERT INTO {table_name} ({', '.join(fields)}) VALUES ({', '.join(values)});"
        return {'status': 'success', 'message': sql}
    
    except json.JSONDecodeError:
        return {'status': 'error', 'message': "错误：无效的JSON格式"}
    except Exception as e:
        return {'status': 'error', 'message': f"错误：{str(e)}"}

def execute_sql(sql: str) -> dict:
    """
    执行 SQL 语句（只允许 INSERT 或 UPDATE）
    :param sql: SQL语句
    :return: {"status": "success/error", "message": "..."}
    """
    # 安全检查
    if not sql.lower().startswith(("insert", "update")):
        return {"status": "error", "message": "仅允许执行 INSERT 或 UPDATE 语句"}

    # 数据库配置
    config = {
        "host": DB_HOST,
        "user": DB_USER,
        "password": DB_PASSWORD,
        "database": DB_NAME,
        "port": DB_PORT,
        "charset": DB_CHARSET
    }

    try:
        connection = pymysql.connect(**config)
        with connection.cursor() as cursor:
            cursor.execute(sql)
        connection.commit()
        return {"status": "success", "message": "SQL 执行成功"}
    except pymysql.Error as e:
        return {"status": "error", "message": f"数据库错误: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"系统错误: {str(e)}"}
    finally:
        if 'connection' in locals() and connection:
            connection.close()


@app.route("/exec-sql", methods=["POST"])
def exec_sql():
    """
    POST /exec-sql
    Body:
    {
        "data": json字符串
    }
    """
    # 从POST请求中获取JSON数据
    try:
        request_data = request.get_json()
        if not request_data or "data" not in request_data:
            return jsonify({
                "status": "error",
                "message": "请求体中缺少 'data' 字段"
            }), 400
        # print(request_data) # {'data':}
        
        # 获取JSON字符串
        json_data = request_data["data"]
        # print(json_data)  # {'object': '动物', ...}
        
        # 生成SQL语句
        generate_result = generate_sql(json_data)
        
        # 检查生成结果
        if generate_result["status"] != "success":
            return jsonify(generate_result), 400
        # 获取生成的SQL语句
        sql = generate_result["message"]
        
        # 执行SQL
        execute_result = execute_sql(sql)
        
        # 返回执行结果
        if execute_result["status"] == "success":
            return jsonify({
                "status": "success",
                "message": "操作成功",
                "sql": sql
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": execute_result["message"],
                "sql": sql
            }), 500
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"请求处理错误: {str(e)}"
        }), 500
        
        
        
    # """
    # POST /exec-sql
    # Body:
    # {
    #     "data": json文件
    # }
    # """
    # # data = request.get_json(silent=True)
    # data = request.args.get("data")
    # print(data)
    # if not data or "data" not in data:
    #     return jsonify({"status": "error", "message": "请求体中缺少 'sql'"}), 400

    # sql = data["sql"]
    # result = execute_sql(sql)
    # return jsonify(result), 200 if result["status"] == "success" else 500

if __name__ == "__main__":
    # 启动 Flask 服务
    app.run(host="0.0.0.0", port=5000, debug=True)

# {"data":
# 	{
# 	"object": "动物",
# 	"animal": "驼鹿",
# 	"count": 1,
# 	"behavior": "正在吃草",
# 	"status": "健康，自然状态",
# 	"percentage": 25,
# 	"confidence": 95,
# 	"caption": "图中展示了一只驼鹿在吃草",
# 	"image_id":"08997y8y",
# 	"sensor_id":"ihoioioijoi",
# 	"location":"成都",
# 	"longitude":"133.25",
# 	"latitude":"35.5",
# 	"time":"0325",
# 	"date":"20050726",
# 	"insert_time":"0326"
# 	}   
# }

# SELECT * FROM image_info WHERE animal = '狗';
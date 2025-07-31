# app.py
from flask import Flask, request, jsonify
from mysql_insert.sql_generator import generate_sql
from mysql_insert.sql_insert import execute_sql

app = Flask(__name__)

@app.route("/exec-sql", methods=["POST"])
def exec_sql():
    """
    POST /exec-sql
    """
    # 从POST请求中获取JSON数据
    try:
        request_data = request.get_json()
        if not request_data or "data" not in request_data:
            return jsonify({
                "status": "error", 
                "message": "请求体中缺少 'data' 字段"
            }), 400
        print("request_data:", request_data) # {'data':}
        
        # 获取JSON字符串
        json_data = request_data["data"]
        print(json_data)  # {'object': '动物', ...}
        
        # 生成SQL语句
        generate_result = generate_sql(json_data)
        print(generate_result)
        
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

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
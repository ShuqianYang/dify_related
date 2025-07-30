from flask import Flask, request, jsonify
from mysql_query.sql_query import query_sql

app = Flask(__name__)

@app.route("/query-sql", methods=["POST"])
def exec_query_sql():
    """
    POST /query-sql
    """
    # 从POST请求中获取JSON数据
    try:
        request_data = request.get_json()
        if not request_data or "query" not in request_data:
            return jsonify({
                "status": "error", 
                "message": "请求体中缺少 'query' 字段"
            }), 400
        print(request_data) # {'query':}
        
        # 获取查询语句
        query = request_data["query"]

        if not query:
            return jsonify({
                "status": "error", 
                "message": "查询语句不能为空"
            }), 400 
        print(query) 
              
        # 执行SQL
        execute_result = query_sql(query)
        
        # 返回执行结果
        if execute_result["status"] == "success":
            return jsonify({
                "status": "success",
                "data": execute_result["data"]
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": execute_result["message"]
            }), 500

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"请求处理错误: {str(e)}"
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

# {"query":"SELECT * FROM `国家重点保护野生动物名录` WHERE 中文名 = '马';}

# {
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
# }  
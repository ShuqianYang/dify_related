def main(arg: str) -> dict:
    arg = json.loads(arg)
    query_animal = arg["animal"]
    print(query_animal)
    query_sql = f"SELECT * FROM `国家重点保护野生动物名录` WHERE 中文名 = '{query_animal}'"
    return {
        "result": query_sql
    }

arg =  {
	"object": "动物",
	"animal": "驼鹿",
	"count": 1,
	"behavior": "正在吃草",
	"status": "健康，自然状态",
	"percentage": 25,
	"confidence": 95,
	"caption": "图中展示了一只驼鹿在吃草",
	"image_id":"08997y8y",
	"sensor_id":"ihoioioijoi",
	"location":"成都",
	"longitude":"133.25",
	"latitude":"35.5",
	"time":"0325",
	"date":"20050726",
	"insert_time":"0326"
}  

result = main(arg)
print(result)
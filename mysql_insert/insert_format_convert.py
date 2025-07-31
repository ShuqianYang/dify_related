import json
def main(arg:dict, image_id:str, sensor_id:str, location:str, longitude:str, latitude:str, time:str, date:str) -> dict:
    # 将一个 JSON 格式的字符串 arg 解析为对应的 Python 对象
    # arg = json.loads(arg) 
    arg.update({"location":location, "longitude":longitude, "latitude":latitude, "time":time, "date":date, "image_id":image_id, "sensor_id":sensor_id})
    return {
        "result": arg  # 输出格式object
    }
    

arg = {
	"object": "动物",
	"animal": "扬子鳄",
	"count": 1,
	"behavior": "正在游泳",
	"status": "健康，自然状态",
	"percentage": 25,
	"confidence": 95,
	"caption": "图中展示了一只扬子鳄在游泳"
	}
image_id = "08997y8y"
sensor_id = "ihoioioijoi"
location = "成都"
longitude = "183.75"
latitude = "88.5"
time = "0325"
date = "20050726"



result = main(arg, image_id, sensor_id, location, longitude, latitude, time, date)
print(result["result"])

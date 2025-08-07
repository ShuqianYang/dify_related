# sql_generator.py
import json

def generate_sql(data: dict) -> dict:
    """
    将JSON数据转换为MySQL INSERT语句
    """
    try:
        table_name = "image_info"
        required_fields = ['object', 'count', 'behavior', 'status', 'percentage', 'confidence', 'caption', 'image_id', 'sensor_id', 'location', 'longitude', 'latitude', 'time', 'date']
        optional_fields = ['animal', 'insert_time']

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

if __name__ == "__main__":
    # 测试 generate_sql 函数
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
        "insert_time": "0326"
    }

    result = generate_sql(test_data)
    print(result)
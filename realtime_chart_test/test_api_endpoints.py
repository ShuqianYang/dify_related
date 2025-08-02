# 测试所有API端点

import requests
import json

def test_api_endpoints():
    """测试所有API端点"""
    base_url = "http://127.0.0.1:5003"
    
    endpoints = [
        "/api/animal-list",
        "/api/chart-data", 
        "/api/location-data",
        "/api/timeseries-data"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\n测试端点: {endpoint}")
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            else:
                print(f"错误响应: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"请求错误: {e}")
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            print(f"原始响应: {response.text}")

if __name__ == "__main__":
    test_api_endpoints()
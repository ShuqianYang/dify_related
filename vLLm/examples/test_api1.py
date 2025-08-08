# 方式二：部署为在线 API 服务（最常用）
    # 方法1：使用http方式调用
"""
优点：
1. 通用性强：这种方法不依赖任何特定的客户端库，理论上任何支持 HTTP 请求的编程语言（如 Java, Node.js, Go 等）都可以用这种方式调用 vLLM 服务。
2. 透明度高：你可以清楚地看到请求是如何构建和发送的，以及服务器返回的原始 JSON 数据。
缺点：
1. 代码繁琐：你需要手动处理请求的构建、发送、错误检查和 JSON 数据的解析，这在处理复杂的 API 调用时会显得冗长。
"""
import requests
import json

url = "http://localhost:8000/v1/completions"
headers = {"Content-Type": "application/json"}

data = {
    "model": "meta-llama/Llama-2-7b-chat-hf",
    "prompt": "中国的首都是哪里？", # 你可以问中文
    "max_tokens": 100,
    "temperature": 0.2
}

response = requests.post(url, headers=headers, data=json.dumps(data))

if response.status_code == 200:
    result = response.json()
    print("模型回答:", result['choices'][0]['text'])
else:
    print("请求失败:", response.status_code, response.text)
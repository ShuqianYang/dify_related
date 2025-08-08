# 方式二：部署为在线 API 服务（最常用）
    # 方法2：使用 openai 库（OpenAI 兼容 API）
"""
优点：
1. 通用性强：这种方法不依赖任何特定的客户端库，理论上任何支持 HTTP 请求的编程语言（如 Java, Node.js, Go 等）都可以用这种方式调用 vLLM 服务。
2. 透明度高：你可以清楚地看到请求是如何构建和发送的，以及服务器返回的原始 JSON 数据。
缺点：
1. 代码繁琐：你需要手动处理请求的构建、发送、错误检查和 JSON 数据的解析，这在处理复杂的 API 调用时会显得冗长。
"""
from openai import OpenAI
# Set OpenAI's API key and API base to use vLLM's API server.
openai_api_key = "EMPTY"
openai_api_base = "http://localhost:8000/v1"

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

chat_response = client.chat.completions.create(
    model="Qwen/Qwen3-8B",
    messages=[
        {"role": "user", "content": "Give me a short introduction to large language models."},
    ],
    max_tokens=32768,
    temperature=0.6,
    top_p=0.95,
    extra_body={
        "top_k": 20,
        "chat_template_kwargs": {"enable_thinking": False},  # 思考功能关闭
    },
)
print("Chat response:", chat_response)
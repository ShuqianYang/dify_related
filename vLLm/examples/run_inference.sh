# 方式二：部署为在线 API 服务（最常用）
python -m vllm.entrypoints.api_server \
    --model "meta-llama/Llama-2-7b-chat-hf" \
    --port 8000
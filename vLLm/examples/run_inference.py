# 方式一：离线批量处理（写 Python 脚本）
from vllm import LLM, SamplingParams

# 准备一些要提问的句子
prompts = [
    "Hello, my name is",
    "The president of the United States is",
    "The capital of France is",
    "The future of AI is",
]

# 定义采样参数 (Sampling Parameters)
    # 这会影响模型的创造性、随机性等
    # temperature=0 表示更确定性的回答，越高越随机
    # top_p 控制了生成单词的选择范围
sampling_params = SamplingParams(temperature=0.8, top_p=0.95)

# 1. 从 Hugging Face 加载模型
    # 将 "model_name_or_path" 替换成你的模型ID
    # vLLM 会自动下载模型
llm = LLM(model="Qwen/Qwen3-8B") # 第一次运行会需要一些时间下载模型

# 2. 生成文本
    # 使用 llm.generate() 方法来处理所有提问
outputs = llm.generate(prompts, sampling_params)

# 3. 打印结果
for output in outputs:
    prompt = output.prompt
    generated_text = output.outputs[0].text
    print(f"Prompt: {prompt!r}, Generated: {generated_text!r}")
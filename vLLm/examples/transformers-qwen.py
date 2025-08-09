"""
流程：
1. 加载：加载分词器和模型
2. 构建输入
3. 预处理：
    1. 输入文本转换 tokenizer.apply_chat_template
    2. 输入分词器
4. 推理：进行文本生成
5. 后处理：解析输出内容，去除输入和思考的部分
"""

from transformers import AutoModelForCausalLM, AutoTokenizer

# 模型路径配置 - 可以是本地路径或Hugging Face模型名称
MODEL_PATH = "Qwen/Qwen3-8B"  # 可以修改为本地模型路径，如: "/path/to/your/local/model"

# load the tokenizer and the model
    # 用于加载与模型相匹配的分词器
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    # 用于加载任何"因果语言模型"
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    torch_dtype="auto",
    device_map="auto"
)


# prepare the model input
prompt = "Give me a short introduction to large language model."
messages = [
    {"role": "user", "content": prompt}
]
"""
Hugging Face Transformers 库中处理对话或多轮交互时常用的格式，也被称为 “对话模板”（chat template） 格式。
"user" 表示来自用户的输入或请求。
"assistant" 表示模型的回答或响应。当你需要向模型提供对话历史，以便让它记住之前的对话并在此基础上继续时，就会用到这个角色。
"system" 来给模型提供全局指令或背景信息。它通常用于设置对话的基调、规则或角色。system 消息会贯穿整个对话，影响模型的所有后续响应，但它不会像 user 和 assistant 那样被视为对话的一部分。
常见用途包括：
    1. 设定角色：让模型扮演一个特定的角色，比如“你是一位专业的历史学家。”
    2. 限制行为：告诉模型“回答必须保持简洁，不超过两句话。”
    3. 提供背景知识： 给出一些重要的背景信息，比如“以下所有对话都将围绕公司的财务数据展开。”
"""
    # 它将结构化的 messages 列表转换为模型期望的单个字符串输入。（apply_chat_template函数用于特定模型的模板转换）
input = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True,
    enable_thinking=True # Switches between thinking and non-thinking modes. Default is True.
)
    # 传入分词器
model_inputs = tokenizer([input], return_tensors="pt").to(model.device)


# conduct text completion
    # 生成文本
generated_ids = model.generate(
    **model_inputs,
    max_new_tokens=32768
)
output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist() 


# parsing thinking content
try:
    # rindex finding 151668 (</think>)
    index = len(output_ids) - output_ids[::-1].index(151668)
except ValueError:
    index = 0
    # 解析think标签
thinking_content = tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
    # 解析content标签
content = tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")

print("thinking content:", thinking_content)
print("content:", content)

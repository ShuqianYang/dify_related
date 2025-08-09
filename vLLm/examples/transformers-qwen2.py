"""
两轮对话流程：
1. 加载：加载分词器和模型
2. 第一轮对话：
    1. 构建第一轮输入
    2. 预处理和推理
    3. 解析输出并保存到对话历史
3. 第二轮对话：
    1. 构建包含历史的第二轮输入
    2. 预处理和推理
    3. 解析输出
4. 显示完整对话历史
"""

from transformers import AutoModelForCausalLM, AutoTokenizer

# 模型路径配置 - 可以是本地路径或Hugging Face模型名称
MODEL_PATH = "Qwen/Qwen3-8B"  # 可以修改为本地模型路径，如: "/path/to/your/local/model"

# load the tokenizer and the model
print("正在加载模型...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    torch_dtype="auto",
    device_map="auto"
)
print("模型加载完成！")

def chat_with_model(messages, tokenizer, model, max_new_tokens=1024):
    """
    与模型进行单轮对话的函数
    
    Args:
        messages: 对话历史列表
        tokenizer: 分词器
        model: 模型
        max_new_tokens: 最大生成token数
    
    Returns:
        tuple: (thinking_content, content) - 思考内容和回复内容
    """
    # 将结构化的 messages 列表转换为模型期望的单个字符串输入
    input_text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=True  # 启用思考模式
    )
    
    # 传入分词器
    model_inputs = tokenizer([input_text], return_tensors="pt").to(model.device)
    
    # 进行文本生成
    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=max_new_tokens,
        do_sample=True,
        temperature=0.7,
        top_p=0.8
    )
    
    # 提取新生成的token
    output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()
    
    # 解析思考内容和回复内容
    try:
        # 查找 </think> 标签的位置 (token id: 151668)
        index = len(output_ids) - output_ids[::-1].index(151668)
    except ValueError:
        index = 0
    
    # 解析think标签内容
    thinking_content = tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
    # 解析实际回复内容
    content = tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")
    
    return thinking_content, content

# 初始化对话历史
conversation_history = []

# 第一轮对话
print("\n" + "="*50)
print("第一轮对话")
print("="*50)

first_prompt = "请简单介绍一下大语言模型是什么？"
print(f"用户: {first_prompt}")

# 添加第一轮用户输入到对话历史
conversation_history.append({"role": "user", "content": first_prompt})

# 获取第一轮回复
thinking1, response1 = chat_with_model(conversation_history, tokenizer, model)

print(f"\n模型思考过程: {thinking1}")
print(f"模型回复: {response1}")

# 将模型回复添加到对话历史
conversation_history.append({"role": "assistant", "content": response1})

# 第二轮对话
print("\n" + "="*50)
print("第二轮对话")
print("="*50)

second_prompt = "那么大语言模型有哪些实际应用场景呢？"
print(f"用户: {second_prompt}")

# 添加第二轮用户输入到对话历史
conversation_history.append({"role": "user", "content": second_prompt})

# 获取第二轮回复（包含完整对话历史）
thinking2, response2 = chat_with_model(conversation_history, tokenizer, model)

print(f"\n模型思考过程: {thinking2}")
print(f"模型回复: {response2}")

# 将第二轮回复添加到对话历史
conversation_history.append({"role": "assistant", "content": response2})

# 显示完整对话历史
print("\n" + "="*50)
print("完整对话历史")
print("="*50)

for i, message in enumerate(conversation_history):
    role = "用户" if message["role"] == "user" else "助手"
    print(f"{i+1}. {role}: {message['content']}")
    print()

print("对话结束！")

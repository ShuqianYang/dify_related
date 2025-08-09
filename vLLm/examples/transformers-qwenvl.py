"""
1. 加载：加载模型和处理器
2. 构建输入
3. 预处理：
    1. 输入文本转换 tokenizer.apply_chat_template
    2. 提取图像和视频信息
    3. 将处理后的文本、图像和视频输入分词器
4. 推理：进行回答生成
5. 后处理：解析输出内容，去除输入和思考的部分
"""

from modelscope import Qwen2_5_VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from qwen_vl_utils import process_vision_info
# qwen_vl_utils.process_vision_info：一个工具函数，用于从对话消息中提取图像和视频信息。

#########################################################################################################
## 1. 加载模型和处理器
# default: Load the model on the available device(s)
model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
    "Qwen/Qwen2.5-VL-32B-Instruct", torch_dtype="auto", device_map="auto"
)

# We recommend enabling flash_attention_2 for better acceleration and memory saving, especially in multi-image and video scenarios.
# 使用 flash_attention_2 来加速计算并节省显存
# model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
#     "Qwen/Qwen2.5-VL-32B-Instruct",
#     torch_dtype=torch.bfloat16,
#     attn_implementation="flash_attention_2",
#     device_map="auto",
# )

# default processer
processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-32B-Instruct")

# The default range for the number of visual tokens per image in the model is 4-16384.
# You can set min_pixels and max_pixels according to your needs, such as a token range of 256-1280, to balance performance and cost.
# min_pixels = 256*28*28
# max_pixels = 1280*28*28
# processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-32B-Instruct", min_pixels=min_pixels, max_pixels=max_pixels)


#########################################################################################################
## 2. 构建输入：多模态模型独有输入格式，content包含多种输入类型：
    # 1. 一个图像输入，其值可以是本地路径或网络 URL。
    # 2. 一个文本输入。
messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "image",
                "image": "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-VL/assets/demo.jpeg",
            },
            {"type": "text", "text": "Describe this image."},
        ],
    }
]

#########################################################################################################
## 3. 预处理：
    # 1. 输入文本转换 tokenizer.apply_chat_template
    # 2. 提取图像和视频信息
    # 3. 将处理后的文本、图像和视频输入分词器

# Preparation for inference（apply_chat_template函数用于特定模型的模板转换）
text = processor.apply_chat_template(
    messages, tokenize=False, add_generation_prompt=True
)
# 提取图像和视频信息
image_inputs, video_inputs = process_vision_info(messages)
# 它将处理好的文本、图像和视频数据一起传入，由 processor 将它们全部转换为模型所需的数字张量
inputs = processor(
    text=[text],
    images=image_inputs,
    videos=video_inputs,
    padding=True,
    return_tensors="pt",
)
inputs = inputs.to("cuda")

#########################################################################################################
## 4. 推理
# Inference: Generation of the output
generated_ids = model.generate(**inputs, max_new_tokens=128)

#########################################################################################################
## 5. 后处理
# 通过切片只保留模型新生成的 ID。
generated_ids_trimmed = [
    out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
]
# 解码生成的 ID 序列为文本
output_text = processor.batch_decode(
    generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
)
# skip_special_tokens表示跳过特殊标记
print(output_text)
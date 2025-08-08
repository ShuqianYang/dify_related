import os
import json
import time
from tqdm import tqdm
from PIL import Image
from openai import OpenAI

from .promotion import *
from .tools import  get_file_list, normalize_path
from .pre_process import image_to_base64, contains_chinese, safe_rename
from .params import  PARAMS


def single_inference(image_path, prompt,
        temperature=PARAMS["temperature"], 
        top_p=PARAMS["top_p"], 
        max_tokens=PARAMS["max_tokens"], 
        model="Qwen2.5-VL-3B"):
    """
    单张图像推理
    :param image_path: 图像文件路径
    :param prompt: 提示文本
    :param temperature: 温度参数，控制模型输出的随机性
    :param top_p: top_p参数，控制模型输出的多样性
    :param max_tokens: 最大token数，控制模型输出的长度
    :param model: 模型名称，默认使用Qwen2.5-VL-3B
    :returns:
        包含文本内容和token使用信息的字典
    """
    # 加载模型信息配置文件
    import json
    import os
    model_info_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "files", "lm_model_info.json")
    print("model_info_path:", model_info_path)

    try:
        with open(model_info_path, 'r', encoding='utf-8') as f:
            lm_model_info = json.load(f)
    except Exception as e:
        print(f"加载模型信息配置文件失败: {e}")
        lm_model_info = {}
    
    # 获取模型对应的端口，如果没有找到则使用默认端口11434
    model_port = lm_model_info.get(model, {}).get("port", 11434)
    
    # 构建base_url
    base_url = f"http://localhost:{model_port}/v1"
    print("base_url:", base_url)
    # 初始化模型服务
    client = OpenAI(
        base_url=base_url,
        api_key="wyt")

    response = client.chat.completions.create(
        model=model,
        messages=[{
            "role": "user", 
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_to_base64(image_path)}}]
        }],
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        frequency_penalty=PARAMS["frequency_penalty"],  # 频率惩罚系数，默认0
        presence_penalty=PARAMS["presence_penalty"],  # 存在惩罚系数，默认0
        stop=PARAMS["stop"])
    
    content = response.choices[0].message.content  # 提取核心文本内容
    print("content:", content)

    content_json = content.replace("```json\n", "").replace("\n```", "")
    print("content_json:", content_json)

    # 提取响应数据
    result = {
        "content": json.loads(content_json),
        "tokens": {
            "prompt_tokens": response.usage.prompt_tokens if hasattr(response.usage, "prompt_tokens") else 0,
            "completion_tokens": response.usage.completion_tokens if hasattr(response.usage, "completion_tokens") else 0,
            "total_tokens": response.usage.total_tokens if hasattr(response.usage, "total_tokens") else 0
        }
    }
    # 统计输入给模型的 token 数量、输出模型的 token 数量、总 token 数量
    return result


if __name__ == "__main__":
    image_path = "/mnt/ckpt-chinasatcom-2/wyt/show_system/files/images/animal_image/90.jpg"
    # video_path = "/mnt/ckpt-chinasatcom-2/wyt/show_system/files/images/animal_video/bear.mp4"
    # image_path = "D:/zhijiang/06-Source_Code/show_system/files/images/R-C.png"
    # video_path = "D:/zhijiang/06-Source_Code/show_system/files/images/animal_video/bear.mp4"
    # print(process_single_image(video_path, "描述这个视频"))
    print(single_inference(image_path, PROMOTION_SELECTION_ANIMAL, model="Qwen2.5-VL-7B"))

    # print(get_gpu_memory_usage())
    
    # 图像批量标注
    # batch_inference(
    #     input_dir="D:/zhijiang/06-Source_Code/show_system/images_test", prompt=PROMOTION_SELECTION_ANIMAL,
    #     labeling_file_path="D:/zhijiang/06-Source_Code/show_system/images_test/annotations.jsonl")
    

    # image_paths = get_file_list("C:/Users/chenningyu/Desktop/images", [".jpg", ".png"])
    # print(image_paths)
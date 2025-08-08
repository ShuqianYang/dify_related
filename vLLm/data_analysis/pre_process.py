import os
import re
import cv2
import uuid
import base64
from pathlib import Path


def image_to_base64(image_path, resolution=(448, 448)):
    """将图像转为Base64编码（适配Qwen-VL输入格式）"""
    img = cv2.imread(image_path)
    if img is None: 
        raise FileNotFoundError(f"无法从路径加载图像: {image_path}")
    img = cv2.resize(img, resolution)  # 模型推荐分辨率
    _, buffer = cv2.imencode(".jpg", img)
    
    return "data:image/jpeg;base64," + base64.b64encode(buffer).decode("utf-8")


def draw_bbox_on_image(image_path, bbox, output_path=None):
    """在图像上根据bbox数据绘制边界框
    Args:
        image_path: 原始图像路径
        bbox: 边界框数据字符串，格式为"x,y,width,height"
        output_path: 输出图像路径，默认为原图像目录下的marked_images子目录
    Returns:
        处理后的图像路径
    """
    # 读取图像
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"无法从路径加载图像: {image_path}")
    x, y, width, height = map(int, bbox.split(","))                 # 解析bbox数据
    x2, y2 = x + width, y + height                                  # 计算右下角坐标
    cv2.rectangle(img, (x, y), (x2, y2), (0, 0, 255), 2)            # 绘制边界框（红色，线宽2）
    cv2.imshow("Image with BBox", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    # 生成输出路径
    if not output_path:
        img_dir = os.path.dirname(image_path)                       # 获取原图像目录
        marked_dir = os.path.join(img_dir, "marked_images")         # 创建marked_images目录（如果不存在）
        os.makedirs(marked_dir, exist_ok=True)
        filename = os.path.basename(image_path)                     # 生成输出文件名
        output_path = os.path.join(marked_dir, f"marked_{filename}")

    cv2.imwrite(output_path, img)                                   # 保存绘制后的图像

    return output_path


def contains_chinese(file_path):
    """
    检查字符串是否包含中文字符
    :param text: 待检查的字符串
    :return: 如果包含中文字符返回True，否则返回False
    """
    return bool(re.search(r'[\u4e00-\u9fff]', file_path))


def safe_rename(file_path):
    file_path = Path(file_path)

    if not file_path.is_file():
        return False, "文件不存在"
    
    name = file_path.name
    if not contains_chinese(name):
        return False, "文件名不含中文，无需修改"
    
    parent = file_path.parent
    ext = file_path.suffix
    new_stem = uuid.uuid4().hex[:12]
    new_name = new_stem + ext

    counter = 1
    while (parent / new_name).exists():
        new_name = f"{new_stem}_{counter}{ext}"
        counter += 1

    new_path = parent / new_name
    try:
        file_path.rename(new_path)
        return True, new_name
    except Exception as e:
        return False, str(e)


if __name__ == "__main__":
    image_path = "D:/Downloads/EdgeDownload/2025-07-29_223208_716.png"
    base64_str = image_to_base64(image_path)
    
    draw_bbox_on_image(image_path, "0,10,448,448")

def main(arg: str) -> dict:
    # 将 JSON 字符串 → Python 对象（此处是python字典）
    parsed = json.loads(arg)
    # 将 Python 对象 → JSON 字符串
    pretty = json.dumps(parsed, ensure_ascii=False, indent=2)
    return {
        "result": pretty  # 输出格式string
    }

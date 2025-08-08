# -*- coding: utf-8 -*-
#
# File: params.py
# Author: Yuntao Wang
# Date: 2025-08-07
# Description: 模型调用参数
# 基于南湖平台，通过VLLM完成模型部署

# 模型部署配置
DEPLOY = {
    "local": {
        "url": "http://localhost:10001/v1",
        "api_key": "wyt"
    }
}

# 模型调用参数
PARAMS = {
    "max_tokens": 8192,
    "temperature": 0.5,
    "top_p": 0.9, 
    "frequency_penalty": 0.0, 
    "presence_penalty": 0.0,
    "stop": ["\n\n"]}
# VLLM的使用

参考文献：

- https://openbayes.com/console/public/tutorials/rXxb5fZFr29?utm_source=vLLM-CNdoc&utm_medium=vLLM-CNdoc-V1&utm_campaign=vLLM-CNdoc-V1-25ap
- https://qwen.readthedocs.io/zh-cn/latest/deployment/vllm.html

## 方法一：离线批量处理（写 Python 脚本）

`vLLm\examples\run_inference.py`

## 方法二：

### 运行服务

`vLLm\examples\run_inference.sh`

### 调用

这两种方式的本质区别在于 **调用 API 的客户端库不同** ，但底层调用的都是同一个 vLLM 服务器。

#### 1. 使用 `requests` 库（HTTP 请求）

`vLLm\examples\test_api1.py`

第一种方式直接使用 Python 的 `requests` 库来发送 HTTP 请求。

* **调用方式** ：你手动构建一个 POST 请求，并指定请求的 URL (`http://localhost:8000/v1/completions`)、请求头和 JSON 格式的请求体。
* **优点** ：
* **通用性强** ：这种方法不依赖任何特定的客户端库，理论上任何支持 HTTP 请求的编程语言（如 Java, Node.js, Go 等）都可以用这种方式调用 vLLM 服务。
* **透明度高** ：你可以清楚地看到请求是如何构建和发送的，以及服务器返回的原始 JSON 数据。
* **缺点** ：
* **代码繁琐** ：你需要手动处理请求的构建、发送、错误检查和 JSON 数据的解析，这在处理复杂的 API 调用时会显得冗长。

#### 2. 使用 `openai` 库（OpenAI 兼容 API）

`vLLm\examples\test_api2.py`

第二种方式使用了 `openai` 库，并将其配置为指向 vLLM 的 API 服务器。

* **调用方式** ：vLLM 的 API 服务设计为与 OpenAI 的 API 接口 **兼容** ，因此你可以直接使用 `openai` 官方库来调用 vLLM。你只需要设置 `base_url` 指向 vLLM 服务地址，并指定一个虚拟的 `api_key` (`"EMPTY"`)。
* **优点** ：
* **代码简洁** ：`openai` 库封装了复杂的 HTTP 请求细节，提供了更高级别的、面向对象的方法（例如 `client.chat.completions.create`），使得代码更加简洁易读。
* **功能更丰富** ：这个库通常提供了更好的类型提示、自动补全和错误处理功能，能够提升开发体验。
* **支持更多特性** ：例如，你代码中的 `extra_body` 参数可以用来传递一些特定于模型的参数，比如 Qwen 的 `enable_thinking`，这在手动 `requests` 请求中可能需要更复杂的配置。
* **缺点** ：
* **依赖特定库** ：这种方法需要安装和依赖 `openai` 库，并且只适用于与 OpenAI API 兼容的 API 服务。

---

### 总结

* **`requests` 方式** ：适用于需要最大程度的**灵活性**和**跨语言兼容性**的场景。如果你想从非 Python 环境调用 vLLM，或者需要调试底层的 API 请求，这种方式非常有用。
* **`openai` 方式** ：适用于 **Python 项目** ，并且你希望以一种**更简洁、更高效**的方式来调用 vLLM。由于其强大的功能和与 OpenAI API 的兼容性，这已经成为调用 vLLM 的 **首选方式** 。

两种方式都能够成功调用 vLLM 服务，并获得模型的响应。选择哪一种取决于你的具体需求、项目环境以及你对代码简洁性的偏好。

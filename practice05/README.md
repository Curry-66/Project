# AI 聊天助手（带 AnythingLLM 工具）

## 项目介绍

这是一个基于 LLM 的智能聊天助手，支持使用 curl 工具访问网页和使用 AnythingLLM 工具查询 AnythingLLM 中的文档仓库。

## 功能特性

- 支持终端界面输入聊天内容
- 支持流式输出
- 支持使用 curl 工具访问网页
- 支持使用 AnythingLLM 工具查询文档仓库
- 自动识别关键词，当提到"文档仓库"、"文件仓库"、"仓库"时自动使用 AnythingLLM 工具
- 过滤<think>标签，只显示核心回答内容

## 环境要求

- Python 3.7+
- curl 命令行工具
- 可用的 LLM API（如 OpenAI、智谱 AI 等）
- AnythingLLM 服务（运行在 http://localhost:3001）

## 配置方法

1. 在项目目录中创建 `.env` 文件
2. 填写以下环境变量：

```
# LLM API 配置
BASE_URL=your_llm_api_base_url
MODEL=your_llm_model_name
API_KEY=your_llm_api_key

# AnythingLLM 配置
ANYTHINGLLM_API_KEY=your_anythingllm_api_key
```

## 使用方法

1. 启动 AnythingLLM 服务（确保服务运行在 http://localhost:3001）
2. 运行聊天助手：

```bash
python chat_with_anythingllm.py
```

3. 在终端中输入你的问题，例如：

   - 普通问题：`你好，今天天气怎么样？`
   - 使用 curl 工具：`请访问 https://wttr.in/北京 获取天气信息`
   - 使用 AnythingLLM 工具：`请在文档仓库中查询关于 Python 编程的文档`

4. 输入 `exit` 或按 Ctrl+C 退出聊天

## 工具说明

### 1. curl_request
- **功能**：使用 curl 访问网页并返回内容
- **参数**：
  - `url`：要访问的网页 URL
  - `timeout`：超时时间（可选，默认 30 秒）

### 2. anythingllm_query
- **功能**：调用 AnythingLLM 的聊天 API 查询文档仓库中的信息
- **参数**：
  - `message`：要发送的查询消息
  - `workspace_slug`：工作区标识符（可选，默认 "default"）
  - `timeout`：超时时间（可选，默认 30 秒）

## 注意事项

- 确保 AnythingLLM 服务已经启动并运行在 http://localhost:3001
- 确保 `.env` 文件中的 API 密钥配置正确
- 网络连接稳定，以保证 API 调用的可靠性
- 合理使用工具，避免过度请求

## 示例对话

```
=== AI 聊天助手（带 AnythingLLM 工具）===
输入 'exit' 或按 Ctrl+C 退出聊天
可使用的工具：curl_request, anythingllm_query
当提到'文档仓库'、'文件仓库'、'仓库'时会自动使用 AnythingLLM 工具
============================================================

你: 请访问 https://wttr.in/北京 获取天气信息
助手: [工具调用开始]
curl_request
url: https://wttr.in/北京
[工具调用结束]

[执行工具: curl_request]
Weather report: 北京

     
  ,     
,-.,--.
( (  ),'
 `,`.--'
   `.  

                

[工具执行完成]
助手: 北京的天气信息如下：

[工具执行结果中的天气信息]

你: 请在文档仓库中查询关于 Python 编程的文档
助手: [工具调用开始]
anythingllm_query
message: 请提供关于 Python 编程的文档
workspace_slug: default
[工具调用结束]

[执行工具: anythingllm_query]
{
  "response": "Python 是一种高级编程语言，它具有简单易学的语法，广泛应用于 web 开发、数据科学、人工智能等领域。Python 的主要特点包括：\n1. 简洁易读的语法\n2. 丰富的标准库\n3. 强大的第三方库生态\n4. 跨平台兼容性\n5. 适合快速开发原型"
}

[工具执行完成]
助手: 根据文档仓库中的信息，Python 是一种高级编程语言，具有以下特点：

1. 简洁易读的语法
2. 丰富的标准库
3. 强大的第三方库生态
4. 跨平台兼容性
5. 适合快速开发原型

它广泛应用于 web 开发、数据科学、人工智能等领域。

你: exit
再见！
```

## 故障排除

- **错误：无法加载环境变量**：检查 `.env` 文件是否存在且配置正确
- **错误：API 调用失败**：检查网络连接和 API 密钥是否正确
- **错误：无法访问 AnythingLLM**：确保 AnythingLLM 服务已经启动并运行在 http://localhost:3001
- **错误：工具执行失败**：检查工具参数是否正确，确保目标 URL 或服务可访问

如果遇到其他问题，请检查终端输出的错误信息，或查看 AnythingLLM 的 API 文档获取更多信息。
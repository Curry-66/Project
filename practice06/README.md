# 链式工具调用功能使用说明

## 功能介绍

本项目实现了链式工具调用（Chained Tool Calls）功能，让 LLM 能够根据中间结果自主决定下一步操作，前一个工具的输出可以作为后一个工具的输入参数。

## 核心组件

### 1. ChainedCallContext 类
链式调用上下文管理器，用于在多个工具调用之间传递数据和状态：
- 记录每一步的调用和结果
- 存储中间变量供后续步骤使用
- 设置最大迭代次数，防止无限循环

### 2. execute_chained_tool_call 函数
实现链式工具调用的完整流程：
- 初始化消息历史，包含 system prompt
- 循环最多 max_iterations 次
- 构建分析提示词（包含用户请求和已执行的步骤历史）
- 调用 LLM 决定下一步操作
- 解析 LLM 响应（支持 JSON 格式）
- 如果任务完成，返回最终回答
- 如果需继续调用，执行工具并记录到上下文

### 3. build_analysis_prompt 函数
构建分析提示词，包含：
- 用户原始请求
- 已执行的工具调用历史（工具名、参数、结果）
- 决策规则说明
- JSON 输出格式要求

## 支持的工具

| 工具名称 | 功能 | 参数 |
|---------|------|------|
| curl_request | 使用 curl 访问网页 | url, timeout |
| list_files | 列出目录下的所有文件 | directory |
| read_file | 读取文件内容 | filepath |
| search_files | 搜索目录下包含关键词的文件 | directory, keyword |
| create_file | 创建文件并写入内容 | filepath, content |

## 输出格式

LLM 需要按照以下 JSON 格式返回决策：

### 完成任务时
```json
{"done": true, "answer": "最终回答内容"}
```

### 继续调用工具时
```json
{"done": false, "tool_call": {"name": "工具名称", "arguments": {"参数名": "参数值"}}}
```

## 环境配置

确保已创建 `.env` 文件，包含以下环境变量：
```
BASE_URL=http://localhost:1234/v1
MODEL=Qwen3.5 4B GGUF Q4_K_M
API_KEY=dummy
```

## 使用方法

### 运行聊天助手
```bash
python chat_with_chained_calls.py
```

### 测试脚本
```bash
python test_chained_calls.py
```

## 测试示例

### 测试1：文件搜索链式调用

**用户请求**：
```
请查找 practice02 和 practice05 目录下所有包含'def'关键词的文件，并总结这些文件的主要内容
```

**预期流程**：
1. 搜索 practice02 目录下包含 'def' 的文件
2. 搜索 practice05 目录下包含 'def' 的文件
3. 读取找到的文件内容
4. 总结文件内容并返回

### 测试2：技能查询链式调用

**用户请求**：
```
我想了解 notice 技能的详细规则
```

**预期流程**：
1. 查找 notice 技能的文件位置
2. 读取技能文件内容
3. 总结技能规则并返回

### 测试3：网页处理链式调用

**用户请求**：
```
访问 http://163.com/news/article/KRGTR2H0000189FH.html 并提取页面标题，保存到 practice07/title.txt
```

**预期流程**：
1. 使用 curl_request 访问网页
2. 提取页面标题
3. 创建 practice07/title.txt 文件并保存标题

## 技术特点

- **上下文管理**：通过 ChainedCallContext 类管理调用状态和中间变量
- **动态决策**：LLM 根据中间结果自主决定下一步操作
- **防无限循环**：设置最大迭代次数限制
- **灵活扩展**：支持添加新工具和自定义提示词
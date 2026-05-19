# AI 智能体开发学习项目

这是一个基于 Python 的 AI 智能体开发学习项目，旨在帮助开发者学习和实践 AI 智能体的开发技术。

## 项目结构

```
my_ai_project/
├── src/                 # 源代码目录
│   ├── agent/           # 智能体核心模块
│   ├── utils/           # 工具函数模块
│   ├── __init__.py      # 包初始化
│   └── cli.py           # 命令行接口
├── examples/            # 示例代码目录
├── practice01/          # 练习1：LLM 基础调用
├── practice02/          # 练习2：终端聊天界面
├── practice03/          # 练习3：工具调用功能
├── practice04/          # 练习4：上下文压缩与总结
├── practice05/          # 练习5：5W 信息提取与搜索
├── practice06/          # 练习6：技能调用系统
├── practice07/          # 练习7：链式调用
├── .agents/             # 智能体技能目录
├── output/              # 输出文件目录
├── requirements.txt     # 依赖项配置
├── setup.py             # 项目安装配置
├── .gitignore           # Git 忽略文件
├── env.example          # 环境变量示例
├── report.md            # 项目报告文档
└── README.md            # 项目说明
```

## 环境配置

1. 确保已安装 Python 3.8 或更高版本
2. 创建并激活虚拟环境：
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```
3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
4. 配置环境变量：
   - 复制 `env.example` 为 `.env`
   - 填写 LLM API 密钥等配置信息

## 快速开始

查看 `examples` 目录中的示例代码，了解如何使用本项目的功能。

## 练习模块说明

### practice01 - LLM 基础调用
- **文件**：`llm_client.py`
- **功能**：使用标准 http 库访问 OpenAI 兼容协议的 LLM
- **学习目标**：环境变量读取、HTTP 请求、JSON 数据处理、OpenAI 协议结构

### practice02 - 终端聊天界面
- **文件**：`chat_interface.py`, `tool_chat_client.py`
- **功能**：实现终端聊天界面，支持流式输出和网络访问功能
- **学习目标**：流式输出实现、聊天历史管理、键盘中断处理、工具调用机制

### practice03 - 工具调用功能
- **文件**：`chat_with_tools.py`, `file_tools.py`
- **功能**：实现带文件操作工具调用的终端聊天界面
- **工具列表**：list_files、rename_file、delete_file、create_file、read_file
- **学习目标**：工具调用实现、指令解析、工具执行结果处理

### practice04 - 上下文压缩与总结
- **文件**：`chat_with_summary.py`, `chat_with_5w_and_search.py`
- **功能**：实现带上下文压缩功能的终端聊天界面
- **学习目标**：聊天历史检测、自动总结压缩、token 控制策略

### practice05 - 5W 信息提取与搜索
- **文件**：`chat_with_5w_and_search.py`, `chat_with_summary.py`, `chat_with_anythingllm.py`
- **功能**：从聊天记录中提取 5W 关键信息（Who/What/When/Where/Why）
- **学习目标**：关键信息提取、信息持久化、聊天历史搜索

### practice06 - 技能调用系统
- **文件**：`chat_with_skills.py`, `test_chat.py`, `test_skills.py`
- **功能**：实现技能调用系统，支持多种技能的注册和调用
- **学习目标**：技能系统设计、技能注册机制、测试驱动开发

### practice07 - 链式调用
- **文件**：`chat_with_chained_calls.py`, `test_chained_calls.py`
- **功能**：实现智能体的链式调用能力
- **学习目标**：链式调用模式、多步骤任务处理、复杂任务分解

## 核心模块说明

### src/agent/base.py
- **功能**：定义智能体基类，提供思考和执行动作的抽象方法
- **学习目标**：抽象基类设计、接口定义

### src/agent/example.py
- **功能**：示例智能体实现，展示基类继承和方法实现
- **学习目标**：多态概念、基类实现

### src/utils/helpers.py
- **功能**：通用工具函数，如消息格式化和环境变量加载
- **学习目标**：代码复用、工具模块设计

### src/cli.py
- **功能**：命令行接口，提供打招呼和版本显示功能
- **学习目标**：Click 库使用、命令行参数解析

## 开发指南

- 代码风格：使用 Black 进行代码格式化
- 代码检查：使用 flake8 和 isort 进行代码质量检查
- 测试：使用 pytest 进行单元测试

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。

## 许可证

MIT License

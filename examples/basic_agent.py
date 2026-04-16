from src.agent.example import ExampleAgent

# 创建智能体实例
agent = ExampleAgent(name="学习助手")

# 测试思考功能
prompt = "你好，我想学习 AI 智能体开发"
response = agent.think(prompt)
print("智能体思考结果:")
print(response)
print()

# 测试执行动作功能
action = "搜索 AI 智能体开发教程"
result = agent.act(action)
print("智能体执行结果:")
print(result)

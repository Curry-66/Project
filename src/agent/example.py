from src.agent.base import BaseAgent

class ExampleAgent(BaseAgent):
    """示例智能体"""
    
    def think(self, prompt: str) -> str:
        """思考并生成响应"""
        return f"我是 {self.name}，我收到了你的消息：{prompt}"
    
    def act(self, action: str) -> str:
        """执行动作"""
        return f"我是 {self.name}，我执行了动作：{action}"

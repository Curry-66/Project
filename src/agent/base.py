class BaseAgent:
    """智能体基类"""
    
    def __init__(self, name: str):
        self.name = name
    
    def think(self, prompt: str) -> str:
        """思考并生成响应"""
        raise NotImplementedError
    
    def act(self, action: str) -> str:
        """执行动作"""
        raise NotImplementedError

def format_message(message: str, **kwargs) -> str:
    """格式化消息"""
    return message.format(**kwargs)

def load_env_file(file_path: str) -> dict:
    """加载环境变量文件"""
    env_vars = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except FileNotFoundError:
        pass
    return env_vars

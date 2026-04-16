import os
import json
import http.client

def load_env():
    """加载环境变量"""
    env_vars = {}
    # 使用绝对路径确保能找到 .env 文件
    env_path = os.path.join(os.getcwd(), '.env')
    print(f"Debug: env_path = {env_path}")
    try:
        print(f"Debug: Checking if file exists: {os.path.exists(env_path)}")
        with open(env_path, 'r', encoding='utf-8') as f:
            print("Debug: File opened successfully")
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
                    print(f"Debug: Loaded {key.strip()} = {value.strip()}")
    except FileNotFoundError:
        print(f"Error: .env file not found at {env_path}")
        return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None
    print(f"Debug: Loaded env_vars: {env_vars}")
    return env_vars

def call_llm(prompt, max_tokens=100):
    """使用标准 http 库调用 LLM"""
    env_vars = load_env()
    if not env_vars:
        return "Error: Failed to load environment variables"
    
    base_url = env_vars.get('BASE_URL')
    model = env_vars.get('MODEL')
    api_key = env_vars.get('API_KEY')
    
    if not all([base_url, model, api_key]):
        return "Error: Missing required environment variables"
    
    # 解析 base_url 获取主机和路径
    if base_url.startswith('http://'):
        base_url = base_url[7:]
    elif base_url.startswith('https://'):
        base_url = base_url[8:]
    
    host, path = base_url.split('/', 1)
    path = '/' + path
    
    # 准备请求数据
    data = {
        "model": model,
        "prompt": prompt,
        "max_tokens": max_tokens
    }
    
    # 创建连接
    conn = http.client.HTTPConnection(host)
    
    # 准备请求头
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    try:
        # 发送请求
        conn.request('POST', f'{path}/completions', body=json.dumps(data), headers=headers)
        
        # 获取响应
        response = conn.getresponse()
        
        # 读取响应数据
        response_data = response.read().decode('utf-8')
        
        # 解析响应
        result = json.loads(response_data)
        
        # 提取生成的文本
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['text']
        else:
            return f"Error: Invalid response from LLM: {response_data}"
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        conn.close()

if __name__ == '__main__':
    # 测试调用
    prompt = "Hello, how are you?"
    response = call_llm(prompt)
    print("Prompt:", prompt)
    print("Response:", response)

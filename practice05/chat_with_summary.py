import os
import json
import http.client
import time

MAX_HISTORY_TURNS = 5
MAX_CONTEXT_LENGTH = 3000

def load_env():
    """加载环境变量"""
    env_vars = {}
    env_path = os.path.join(os.getcwd(), '.env')
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except FileNotFoundError:
        print(f"Error: .env file not found at {env_path}")
        return None
    return env_vars

def call_llm(prompt, max_tokens=500):
    """使用标准 http 库调用 LLM"""
    env_vars = load_env()
    if not env_vars:
        print("Error: Failed to load environment variables")
        return None
    
    base_url = env_vars.get('BASE_URL')
    model = env_vars.get('MODEL')
    api_key = env_vars.get('API_KEY')
    
    if not all([base_url, model, api_key]):
        print("Error: Missing required environment variables")
        return None
    
    # 构建提示
    system_prompt = """你是一个简洁的助手，只回答用户的问题，不输出任何其他内容。"""
    full_prompt = f"{system_prompt}\n{prompt}"
    
    # 解析 base_url
    if base_url.startswith('http://'):
        base_url = base_url[7:]
    elif base_url.startswith('https://'):
        base_url = base_url[8:]
    
    try:
        host, path = base_url.split('/', 1)
        path = '/' + path
    except Exception as e:
        print(f"Error: Failed to parse URL: {str(e)}")
        return None
    
    # 准备请求数据
    data = {
        "model": model,
        "prompt": full_prompt,
        "max_tokens": max_tokens,
        "stream": True
    }
    
    try:
        conn = http.client.HTTPConnection(host, timeout=30)
    except Exception as e:
        print(f"Error: Failed to create connection: {str(e)}")
        return None
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    try:
        conn.request('POST', f'{path}/completions', body=json.dumps(data), headers=headers)
        response = conn.getresponse()
        
        response_text = ""
        for line in response:
            line = line.decode('utf-8').strip()
            if line.startswith('data: '):
                data_line = line[6:]
                if data_line == '[DONE]':
                    break
                try:
                    chunk = json.loads(data_line)
                    if 'choices' in chunk and len(chunk['choices']) > 0:
                        text = chunk['choices'][0].get('text', '')
                        response_text += text
                except json.JSONDecodeError:
                    pass
        
        return response_text
    except Exception as e:
        print(f"Error: {str(e)}")
        return None
    finally:
        conn.close()

def filter_response(text):
    """过滤响应，只保留干净的回答"""
    if not text:
        return ""
    
    in_thinking = False
    clean_output = ""
    
    lines = text.split('\n')
    for line in lines:
        if '<think>' in line:
            in_thinking = True
            continue
        if '</think>' in line:
            in_thinking = False
            continue
        if in_thinking:
            continue
        
        if any(keyword in line for keyword in ['Thinking Process:', 'Analyze', 'Role:', 'Task:', 'Constraints:', 'Input from user:', 'System Instructions:']):
            continue
        
        if line.startswith('User:') or line.startswith('Assistant:'):
            continue
        
        if any(keyword in line.lower() for keyword in ['import', 'def', 'class', 'for', 'while', 'if', 'else', 'return', 'print', '/', '.py', 'file', 'path', 'etc', 'home']):
            continue
        
        if line.strip():
            clean_output += line.strip() + ' '
    
    return clean_output.strip()

def calculate_context_length(history):
    """计算当前上下文的总长度"""
    total_length = 0
    for msg in history:
        total_length += len(msg['user']) + len(msg['assistant'])
    return total_length

def summarize_history(history, env_vars):
    """对聊天历史进行总结压缩"""
    print("\n[系统] 检测到聊天历史过长，正在进行上下文压缩...")
    
    # 将历史分为两部分：需要压缩的部分（75%）和保留原文的部分（30%）
    total_turns = len(history)
    compress_end = int(total_turns * 0.7)
    keep_start = int(total_turns * 0.7)
    
    # 构建需要总结的对话
    history_to_summarize = history[:compress_end]
    history_to_keep = history[keep_start:]
    
    # 构建总结提示
    summary_prompt = "请简洁地总结以下对话的主要内容，保留关键信息：\n"
    for msg in history_to_summarize:
        summary_prompt += f"用户：{msg['user']}\n助手：{msg['assistant']}\n"
    
    # 调用 LLM 进行总结
    summary = call_llm(summary_prompt, max_tokens=300)
    summary = filter_response(summary) if summary else ""
    
    # 构建压缩后的历史
    summarized_history = []
    if summary:
        summarized_history.append({
            "user": "[历史总结]",
            "assistant": summary
        })
    
    # 添加保留的原文
    summarized_history.extend(history_to_keep)
    
    print(f"[系统] 上下文压缩完成：从 {total_turns} 轮压缩为 {len(summarized_history)} 条记录")
    
    return summarized_history

def should_summarize(history):
    """判断是否需要触发聊天记录总结"""
    # 检查是否超过5轮
    if len(history) > MAX_HISTORY_TURNS:
        return True
    
    # 检查上下文长度是否超过3k
    if calculate_context_length(history) > MAX_CONTEXT_LENGTH:
        return True
    
    return False

def build_context_prompt(history, current_prompt):
    """构建包含历史记录的完整提示"""
    context_prompt = ""
    
    for msg in history:
        context_prompt += f"用户：{msg['user']}\n助手：{msg['assistant']}\n"
    
    context_prompt += f"用户：{current_prompt}\n助手："
    
    return context_prompt

def call_llm_with_context(prompt, history, max_tokens=500):
    """使用包含历史记录的上下文调用 LLM"""
    env_vars = load_env()
    if not env_vars:
        print("Error: Failed to load environment variables")
        return None
    
    base_url = env_vars.get('BASE_URL')
    model = env_vars.get('MODEL')
    api_key = env_vars.get('API_KEY')
    
    if not all([base_url, model, api_key]):
        print("Error: Missing required environment variables")
        return None
    
    # 构建提示
    system_prompt = """你是一个简洁的助手，只回答用户的问题，不输出任何其他内容。"""
    
    # 如果需要总结，则先总结历史
    if should_summarize(history):
        history = summarize_history(history, env_vars)
    
    # 构建包含历史的完整提示
    full_prompt = f"{system_prompt}\n{build_context_prompt(history, prompt)}"
    
    # 解析 base_url
    if base_url.startswith('http://'):
        base_url = base_url[7:]
    elif base_url.startswith('https://'):
        base_url = base_url[8:]
    
    try:
        host, path = base_url.split('/', 1)
        path = '/' + path
    except Exception as e:
        print(f"Error: Failed to parse URL: {str(e)}")
        return None
    
    # 准备请求数据
    data = {
        "model": model,
        "prompt": full_prompt,
        "max_tokens": max_tokens,
        "stream": True
    }
    
    try:
        conn = http.client.HTTPConnection(host, timeout=30)
    except Exception as e:
        print(f"Error: Failed to create connection: {str(e)}")
        return None
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    try:
        conn.request('POST', f'{path}/completions', body=json.dumps(data), headers=headers)
        response = conn.getresponse()
        
        in_thinking = False
        clean_output = ""
        
        for line in response:
            line = line.decode('utf-8').strip()
            if line.startswith('data: '):
                data_line = line[6:]
                if data_line == '[DONE]':
                    break
                try:
                    chunk = json.loads(data_line)
                    if 'choices' in chunk and len(chunk['choices']) > 0:
                        text = chunk['choices'][0].get('text', '')
                        
                        lines = text.split('\n')
                        for line in lines:
                            if '<think>' in line:
                                in_thinking = True
                                continue
                            if '</think>' in line:
                                in_thinking = False
                                continue
                            if in_thinking:
                                continue
                            
                            if any(keyword in line for keyword in ['Thinking Process:', 'Analyze', 'Role:', 'Task:', 'Constraints:', 'Input from user:', 'System Instructions:']):
                                continue
                            
                            if line.startswith('User:') or line.startswith('Assistant:'):
                                continue
                            
                            if any(keyword in line.lower() for keyword in ['import', 'def', 'class', 'for', 'while', 'if', 'else', 'return', 'print', '/', '.py', 'file', 'path', 'etc', 'home']):
                                continue
                            
                            if line.strip():
                                clean_output += line.strip() + ' '
                                print(line.strip(), end=' ', flush=True)
                                time.sleep(0.05)
                except json.JSONDecodeError:
                    pass
        
        return clean_output.strip() if clean_output else None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None
    finally:
        conn.close()

def main():
    """主函数，实现终端聊天界面"""
    print("=== AI 聊天助手（支持上下文压缩）===")
    print(f"当聊天历史超过 {MAX_HISTORY_TURNS} 轮或上下文长度超过 {MAX_CONTEXT_LENGTH} 字符时，将自动进行上下文压缩")
    print("输入 'exit' 或按 Ctrl+C 退出聊天")
    print("=" * 50)
    
    # 初始化聊天历史
    history = []
    
    try:
        while True:
            # 获取用户输入
            user_input = input("\n你: ")
            
            # 检查是否退出
            if user_input.strip().lower() == 'exit':
                print("再见！")
                break
            
            # 显示助手正在输入
            print("助手: ", end='', flush=True)
            
            # 调用 LLM 获取响应（带上下文管理）
            assistant_response = call_llm_with_context(user_input, history)
            
            # 添加到历史记录
            if assistant_response:
                history.append({
                    "user": user_input,
                    "assistant": assistant_response
                })
                
                # 显示当前状态
                print(f"\n[状态] 当前对话轮次: {len(history)}, 上下文长度: {calculate_context_length(history)}")

    except KeyboardInterrupt:
        print("\n再见！")

if __name__ == '__main__':
    main()

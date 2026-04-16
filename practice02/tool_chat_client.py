# -*- coding: utf-8 -*-
import os
import json
import http.client
import time
import sys
import subprocess

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
        print(f"错误: 在 {env_path} 未找到 .env 文件")
        return None
    return env_vars

def curl_request(url, timeout=30):
    """使用 curl 访问网页并返回内容
    
    Args:
        url (str): 要访问的网页 URL
        timeout (int): 超时时间（秒）
    
    Returns:
        str: 网页内容或错误信息
    """
    try:
        # 构建 curl 命令
        cmd = [
            'curl',
            '-s',  # 静默模式
            '-m', str(timeout),  # 超时时间
            '-L',  # 跟随重定向
            url
        ]
        
        # 执行 curl 命令
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        # 检查执行结果
        if result.returncode == 0:
            return result.stdout
        else:
            return f"错误: curl 执行失败 (代码 {result.returncode}): {result.stderr}"
    except Exception as e:
        return f"错误: {str(e)}"

def execute_tool(tool_name, parameters):
    """执行工具调用
    
    Args:
        tool_name (str): 工具名称
        parameters (dict): 工具参数
    
    Returns:
        str: 工具执行结果
    """
    try:
        if tool_name == "curl_request":
            url = parameters.get("url")
            timeout = parameters.get("timeout", 30)
            return curl_request(url, timeout)
        else:
            return f"错误: 未知工具 '{tool_name}'"
    except Exception as e:
        return f"错误: {str(e)}"

def call_llm(prompt, max_tokens=1000):
    """使用标准 http 库调用 LLM"""
    env_vars = load_env()
    if not env_vars:
        print("错误: 无法加载环境变量")
        return

    base_url = env_vars.get('BASE_URL')
    model = env_vars.get('MODEL')
    api_key = env_vars.get('API_KEY')

    if not all([base_url, model, api_key]):
        print("错误: 缺少必要的环境变量")
        return

    # 系统提示词 - 包含工具调用说明
    system_prompt = """你是一个智能助手，可以使用以下工具来执行网络访问：

工具列表：
1. curl_request
   - 功能：使用 curl 访问网页并返回内容
   - 参数：
     - url: 要访问的网页 URL
     - timeout: 超时时间（可选，默认 30 秒）

使用工具的格式：
当你需要使用工具时，请按照以下格式输出：

[工具调用开始]
工具名称
参数1: 值1
参数2: 值2
...
[工具调用结束]

例如：
[工具调用开始]
curl_request
url: https://www.example.com
timeout: 10
[工具调用结束]

当工具执行完成后，我会返回执行结果，你需要基于结果继续与用户对话。"""

    full_prompt = f"{system_prompt}\n\n用户问：{prompt}\n\n助手回答："

    # 解析 base_url
    if base_url.startswith('http://'):
        base_url = base_url[7:]
    elif base_url.startswith('https://'):
        base_url = base_url[8:]

    try:
        host, path = base_url.split('/', 1)
        path = '/' + path
    except Exception as e:
        print(f"错误: 解析 URL 失败: {str(e)}")
        return

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
        print(f"错误: 创建连接失败: {str(e)}")
        return

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
                        if text:
                            response_text += text
                except json.JSONDecodeError:
                    pass

        # 处理工具调用
        if "[工具调用开始]" in response_text and "[工具调用结束]" in response_text:
            # 提取工具调用部分
            tool_call_start = response_text.find("[工具调用开始]") + len("[工具调用开始]")
            tool_call_end = response_text.find("[工具调用结束]")
            tool_call_content = response_text[tool_call_start:tool_call_end].strip()
            
            # 解析工具名称和参数
            lines = tool_call_content.split('\n')
            tool_name = lines[0].strip()
            parameters = {}
            
            for line in lines[1:]:
                if ':' in line:
                    key, value = line.split(':', 1)
                    parameters[key.strip()] = value.strip()
            
            # 执行工具
            print(f"\n[执行工具: {tool_name}]")
            tool_result = execute_tool(tool_name, parameters)
            # 限制输出长度，避免内容过长
            if len(tool_result) > 1000:
                tool_result = tool_result[:1000] + "...（内容过长，已截断）"
            print(tool_result)
            print("[工具执行完成]")
            
            # 基于工具执行结果继续对话
            follow_up_prompt = f"\n工具执行结果：\n{tool_result}\n\n请基于以上结果继续与用户对话："
            call_llm(follow_up_prompt, max_tokens=500)
        else:
            # 直接输出回答
            if response_text.strip():
                print(response_text.strip())
            else:
                print("抱歉，我无法回答这个问题。")
    except Exception as e:
        print(f"错误: {str(e)}")
    finally:
        conn.close()

def main():
    """主函数，实现终端聊天界面"""
    # 确保终端使用 UTF-8 编码
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("=== AI 聊天助手（带 curl 工具）===")
    print("输入 'exit' 或按 Ctrl+C 退出聊天")
    print("可使用的工具：curl_request")
    print("=" * 60)

    try:
        while True:
            user_input = input("\n你: ")

            if user_input.strip().lower() == 'exit':
                print("再见！")
                break

            print("助手: ", end='', flush=True)
            call_llm(user_input)

    except KeyboardInterrupt:
        print("\n再见！")

if __name__ == '__main__':
    main()

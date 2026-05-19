# -*- coding: utf-8 -*-
import os
import json
import http.client
import time
import sys
import subprocess

MAX_HISTORY_TURNS = 5
MAX_CONTEXT_LENGTH = 3000
LOG_FILE_PATH = os.path.join(os.getcwd(), 'chat_log.txt')

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
            '-H', 'Accept-Language: zh-CN,zh;q=0.9',  # 设置语言
            url
        ]
        
        # 执行 curl 命令，不使用 text=True，避免编码问题
        result = subprocess.run(
            cmd,
            capture_output=True,
            check=False
        )
        
        # 检查执行结果
        if result.returncode == 0:
            # 尝试使用 UTF-8 解码，如果失败则使用 GBK
            try:
                return result.stdout.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    return result.stdout.decode('gbk')
                except UnicodeDecodeError:
                    return f"错误: 无法解码网页内容"
        else:
            # 尝试解码错误信息
            try:
                stderr = result.stderr.decode('utf-8', errors='replace')
            except:
                stderr = "无法读取错误信息"
            return f"错误: curl 执行失败 (代码 {result.returncode}): {stderr}"
    except Exception as e:
        return f"错误: {str(e)}"

def get_anythingllm_workspaces(timeout=30):
    """获取 AnythingLLM 可用的工作区列表
    
    Args:
        timeout (int): 超时时间（秒）
    
    Returns:
        str: 工作区列表或错误信息
    """
    try:
        env_vars = load_env()
        if not env_vars:
            return "错误: 无法加载环境变量"
        
        anythingllm_api_key = env_vars.get('ANYTHINGLLM_API_KEY')
        if not anythingllm_api_key:
            return "错误: 缺少 ANYTHINGLLM_API_KEY 环境变量"
        
        # 构建 curl 命令
        cmd = [
            'curl',
            '-s',  # 静默模式
            '-m', str(timeout),  # 超时时间
            '-X', 'GET',  # GET 请求
            '-H', f'Authorization: Bearer {anythingllm_api_key}',  # API 密钥认证
            'http://localhost:3001/api/v1/workspaces'  # API 地址（复数形式）
        ]
        
        # 执行 curl 命令
        result = subprocess.run(
            cmd,
            capture_output=True,
            check=False
        )
        
        # 检查执行结果
        if result.returncode == 0:
            # 尝试使用 UTF-8 解码
            try:
                return result.stdout.decode('utf-8')
            except UnicodeDecodeError:
                return f"错误: 无法解码响应内容"
        else:
            # 尝试解码错误信息
            try:
                stderr = result.stderr.decode('utf-8', errors='replace')
            except:
                stderr = "无法读取错误信息"
            return f"错误: API 调用失败 (代码 {result.returncode}): {stderr}"
    except Exception as e:
        return f"错误: {str(e)}"

def anythingllm_query(message, workspace_slug="default", timeout=30):
    """使用 curl 调用 AnythingLLM 的聊天 API
    
    Args:
        message (str): 要发送的查询消息
        workspace_slug (str): 工作区标识符，默认为 "default"
        timeout (int): 超时时间（秒）
    
    Returns:
        str: API 响应内容或错误信息
    """
    try:
        env_vars = load_env()
        if not env_vars:
            return "错误: 无法加载环境变量"
        
        anythingllm_api_key = env_vars.get('ANYTHINGLLM_API_KEY')
        if not anythingllm_api_key:
            return "错误: 缺少 ANYTHINGLLM_API_KEY 环境变量"
        
        # 构建 curl 命令
        cmd = [
            'curl',
            '-s',  # 静默模式
            '-m', str(timeout),  # 超时时间
            '-X', 'POST',  # POST 请求
            '-H', f'Authorization: Bearer {anythingllm_api_key}',  # API 密钥认证
            '-H', 'Content-Type: application/json',  # JSON 内容类型
            '-d', json.dumps({'message': message}),  # 发送的消息
            f'http://localhost:3001/api/v1/workspace/{workspace_slug}/chat'  # API 地址
        ]
        
        # 执行 curl 命令
        result = subprocess.run(
            cmd,
            capture_output=True,
            check=False
        )
        
        # 检查执行结果
        if result.returncode == 0:
            # 尝试使用 UTF-8 解码
            try:
                return result.stdout.decode('utf-8')
            except UnicodeDecodeError:
                return f"错误: 无法解码响应内容"
        else:
            # 尝试解码错误信息
            try:
                stderr = result.stderr.decode('utf-8', errors='replace')
            except:
                stderr = "无法读取错误信息"
            
            # 错误代码 28 通常是超时错误
            if result.returncode == 28:
                return f"错误: API 调用超时 (代码 {result.returncode})。请检查：1. AnythingLLM 是否正在运行 2. API 地址是否正确 3. 网络连接是否正常"
            else:
                return f"错误: API 调用失败 (代码 {result.returncode}): {stderr}"
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
        elif tool_name == "anythingllm_query":
            message = parameters.get("message")
            workspace_slug = parameters.get("workspace_slug", "default")
            timeout = parameters.get("timeout", 30)
            return anythingllm_query(message, workspace_slug, timeout)
        elif tool_name == "get_anythingllm_workspaces":
            timeout = parameters.get("timeout", 30)
            return get_anythingllm_workspaces(timeout)
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
    system_prompt = """你是一个智能助手，可以使用以下工具：

工具列表：
1. curl_request
   - 功能：使用 curl 访问网页并返回内容
   - 参数：
     - url: 要访问的网页 URL
     - timeout: 超时时间（可选，默认 30 秒）

2. anythingllm_query
   - 功能：调用 AnythingLLM 的聊天 API 查询文档仓库中的信息
   - 参数：
     - message: 要发送的查询消息
     - workspace_slug: 工作区标识符（可选，默认 "default"）
     - timeout: 超时时间（可选，默认 30 秒）

3. get_anythingllm_workspaces
   - 功能：获取 AnythingLLM 中可用的工作区列表
   - 参数：
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

当工具执行完成后，我会返回执行结果，你需要基于结果继续与用户对话。

使用工具的场景：
- 当用户提到"文档仓库"、"文件仓库"、"仓库"等词汇时，使用 anythingllm_query 工具
- 当用户需要查询 AnythingLLM 中的文档或数据时，使用 anythingllm_query 工具
- 当用户要求访问 AnythingLLM 中的内容时，使用 anythingllm_query 工具
- 当用户需要知道有哪些工作区可用时，使用 get_anythingllm_workspaces 工具
- 当遇到 "Workspace is not a valid workspace" 错误时，先使用 get_anythingllm_workspaces 工具获取可用工作区列表"""

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

        # 过滤<think>标签
        def filter_thinking_tags(text):
            """过滤<think>标签"""
            if '<think>' in text:
                # 移除<think>和</think>之间的内容
                while '<think>' in text and '</think>' in text:
                    start = text.find('<think>')
                    end = text.find('</think>') + len('</think>')
                    text = text[:start] + text[end:]
            return text
        
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
            if tool_result:
                if len(tool_result) > 1000:
                    tool_result = tool_result[:1000] + "...（内容过长，已截断）"
                print(tool_result)
            else:
                tool_result = "错误: 工具执行失败"
                print(tool_result)
            print("[工具执行完成]")
            
            # 基于工具执行结果继续对话
            follow_up_prompt = f"\n工具执行结果：\n{tool_result}\n\n请基于以上结果继续与用户对话："
            call_llm(follow_up_prompt, max_tokens=500)
        else:
            # 直接输出回答，过滤<think>标签
            if response_text.strip():
                filtered_text = filter_thinking_tags(response_text.strip())
                print(filtered_text)
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
    
    print("=== AI 聊天助手（带 AnythingLLM 工具）===")
    print("输入 'exit' 或按 Ctrl+C 退出聊天")
    print("可使用的工具：curl_request, anythingllm_query, get_anythingllm_workspaces")
    print("当提到'文档仓库'、'文件仓库'、'仓库'时会自动使用 AnythingLLM 工具")
    print("输入'获取工作区列表'可查看可用的 AnythingLLM 工作区")
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
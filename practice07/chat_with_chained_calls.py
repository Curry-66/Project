# -*- coding: utf-8 -*-
import os
import json
import http.client
import sys
import subprocess
import io

class ChainedCallContext:
    """链式调用上下文管理器，用于在多个工具调用之间传递数据和状态"""
    
    def __init__(self, max_iterations=5):
        """初始化上下文
        
        Args:
            max_iterations (int): 最大迭代次数，防止无限循环
        """
        self.max_iterations = max_iterations
        self.current_iteration = 0
        self.history = []  # 记录每一步的调用和结果
        self.variables = {}  # 存储中间变量供后续步骤使用
        self.user_request = ""  # 用户原始请求
    
    def reset(self):
        """重置上下文状态"""
        self.current_iteration = 0
        self.history = []
        self.variables = {}
        self.user_request = ""
    
    def add_step(self, tool_name, arguments, result):
        """添加工具调用步骤记录
        
        Args:
            tool_name (str): 工具名称
            arguments (dict): 调用参数
            result (str): 执行结果
        """
        step = {
            "iteration": self.current_iteration,
            "tool_name": tool_name,
            "arguments": arguments,
            "result": result
        }
        self.history.append(step)
        self.current_iteration += 1
    
    def get_history_summary(self):
        """获取历史记录摘要，用于构建提示词"""
        if not self.history:
            return "暂无工具调用历史"
        
        summary = ""
        for i, step in enumerate(self.history):
            summary += f"步骤 {i+1}: 调用工具 '{step['tool_name']}'\n"
            summary += f"  参数: {json.dumps(step['arguments'], ensure_ascii=False)}\n"
            result = step['result']
            if len(result) > 200:
                result = result[:200] + "...(内容过长已截断)"
            summary += f"  结果: {result}\n\n"
        return summary
    
    def has_reached_limit(self):
        """检查是否已达到最大迭代次数"""
        return self.current_iteration >= self.max_iterations
    
    def set_variable(self, name, value):
        """设置中间变量"""
        self.variables[name] = value
    
    def get_variable(self, name, default=None):
        """获取中间变量"""
        return self.variables.get(name, default)

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
        # 尝试从项目根目录加载
        env_path = os.path.join(os.path.dirname(os.getcwd()), '.env')
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
    """使用 curl 访问网页并返回内容"""
    try:
        cmd = [
            'curl',
            '-s',
            '-m', str(timeout),
            '-L',
            '-H', 'Accept-Language: zh-CN,zh;q=0.9',
            url
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            check=False
        )
        
        if result.returncode == 0:
            try:
                return result.stdout.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    return result.stdout.decode('gbk')
                except UnicodeDecodeError:
                    return f"错误: 无法解码网页内容"
        else:
            try:
                stderr = result.stderr.decode('utf-8', errors='replace')
            except:
                stderr = "无法读取错误信息"
            return f"错误: curl 执行失败 (代码 {result.returncode}): {stderr}"
    except Exception as e:
        return f"错误: {str(e)}"

def list_files(directory):
    """列出目录下的所有文件"""
    try:
        if not os.path.exists(directory):
            return f"错误: 目录 '{directory}' 不存在"
        
        files = []
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path):
                files.append(item)
        
        if files:
            return f"目录 '{directory}' 下的文件:\n" + "\n".join(files)
        else:
            return f"目录 '{directory}' 为空"
    except Exception as e:
        return f"错误: {str(e)}"

def read_file(filepath):
    """读取文件内容"""
    try:
        if not os.path.exists(filepath):
            return f"错误: 文件 '{filepath}' 不存在"
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if len(content) > 500:
            content = content[:500] + "...(内容过长已截断)"
        
        return content
    except Exception as e:
        return f"错误: {str(e)}"

def search_files(directory, keyword):
    """搜索目录下包含关键词的文件"""
    try:
        if not os.path.exists(directory):
            return f"错误: 目录 '{directory}' 不存在"
        
        matches = []
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if filename.endswith('.py'):
                    filepath = os.path.join(root, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if keyword in content:
                                matches.append(filepath)
                    except:
                        pass
        
        if matches:
            return f"在目录 '{directory}' 下找到 {len(matches)} 个包含 '{keyword}' 的文件:\n" + "\n".join(matches)
        else:
            return f"在目录 '{directory}' 下未找到包含 '{keyword}' 的文件"
    except Exception as e:
        return f"错误: {str(e)}"

def create_file(filepath, content):
    """创建文件并写入内容"""
    try:
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"文件 '{filepath}' 创建成功"
    except Exception as e:
        return f"错误: {str(e)}"

def execute_tool(tool_name, parameters):
    """执行工具调用"""
    try:
        if tool_name == "curl_request":
            url = parameters.get("url")
            timeout = parameters.get("timeout", 30)
            return curl_request(url, timeout)
        elif tool_name == "list_files":
            directory = parameters.get("directory")
            return list_files(directory)
        elif tool_name == "read_file":
            filepath = parameters.get("filepath")
            return read_file(filepath)
        elif tool_name == "search_files":
            directory = parameters.get("directory")
            keyword = parameters.get("keyword")
            return search_files(directory, keyword)
        elif tool_name == "create_file":
            filepath = parameters.get("filepath")
            content = parameters.get("content")
            return create_file(filepath, content)
        else:
            return f"错误: 未知工具 '{tool_name}'"
    except Exception as e:
        return f"错误: {str(e)}"

def build_analysis_prompt(context):
    """构建分析提示词，包含用户请求和已执行的步骤历史"""
    system_prompt = """你是一个智能助手，可以使用以下工具来完成任务：

可用工具列表：
1. curl_request
   - 功能：使用 curl 访问网页并返回内容
   - 参数：url（要访问的网页URL），timeout（超时时间，可选，默认30秒）

2. list_files
   - 功能：列出目录下的所有文件
   - 参数：directory（目录路径）

3. read_file
   - 功能：读取文件内容
   - 参数：filepath（文件路径）

4. search_files
   - 功能：搜索目录下包含关键词的文件
   - 参数：directory（目录路径），keyword（搜索关键词）

5. create_file
   - 功能：创建文件并写入内容
   - 参数：filepath（文件路径），content（文件内容）

链式调用规则：
- 你可以根据中间结果自主决定下一步操作
- 前一个工具的输出可以作为后一个工具的输入参数
- 如果需要多步操作才能完成任务，请按顺序调用工具
- 每次调用工具后，会返回执行结果，你需要根据结果判断是否继续调用或直接回答用户

决策规则：
1. 分析用户请求，确定需要执行哪些步骤
2. 如果当前信息不足以回答，调用相应工具获取信息
3. 如果已经获得足够信息，直接回答用户问题
4. 如果需要多步操作，依次调用工具，直到完成任务

上下文变量：
- 你可以使用之前工具调用的结果作为后续工具调用的参数
- 在参数中使用 {{变量名}} 的格式引用之前的结果

输出格式要求：
你必须按照以下 JSON 格式输出决策：

1. 完成任务时（直接回答用户，不需要调用工具）：
{"done": true, "answer": "你的最终回答内容"}

2. 继续调用工具时：
{"done": false, "tool_call": {"name": "工具名称", "arguments": {"参数名": "参数值"}}}

示例：
- 搜索文件示例：{"done": false, "tool_call": {"name": "search_files", "arguments": {"directory": "e:/my_ai_project/practice02", "keyword": "def"}}}
- 读取文件示例：{"done": false, "tool_call": {"name": "read_file", "arguments": {"filepath": "e:/my_ai_project/practice02/tool_chat_client.py"}}}
- 完成任务示例：{"done": true, "answer": "根据搜索结果，practice02目录下共有5个Python文件包含'def'关键字。"}

请根据当前状态和用户请求，决定下一步操作。
"""

    user_prompt = f"""
用户请求：{context.user_request}

已执行的步骤：
{context.get_history_summary()}

当前可用变量：{json.dumps(context.variables, ensure_ascii=False)}

请分析当前状态，决定下一步操作。输出必须是有效的JSON格式。
"""

    return system_prompt + user_prompt

def call_llm(prompt, max_tokens=1500):
    """调用LLM获取响应"""
    env_vars = load_env()
    if not env_vars:
        print("错误: 无法加载环境变量")
        return None

    base_url = env_vars.get('BASE_URL')
    model = env_vars.get('MODEL')
    api_key = env_vars.get('API_KEY')

    if not all([base_url, model, api_key]):
        print("错误: 缺少必要的环境变量")
        return None

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
        return None

    data = {
        "model": model,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "stream": False
    }

    try:
        conn = http.client.HTTPConnection(host, timeout=30)
    except Exception as e:
        print(f"错误: 创建连接失败: {str(e)}")
        return None

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    try:
        conn.request('POST', f'{path}/completions', body=json.dumps(data), headers=headers)
        response = conn.getresponse()
        
        response_text = response.read().decode('utf-8')
        try:
            response_json = json.loads(response_text)
            if 'choices' in response_json and len(response_json['choices']) > 0:
                return response_json['choices'][0].get('text', '').strip()
        except json.JSONDecodeError:
            return response_text.strip()
    except Exception as e:
        print(f"错误: {str(e)}")
        return None
    finally:
        conn.close()

def execute_chained_tool_call(user_request, max_iterations=5):
    """执行链式工具调用的完整流程"""
    # 初始化上下文
    context = ChainedCallContext(max_iterations=max_iterations)
    context.user_request = user_request
    
    print(f"=== 开始处理请求: {user_request} ===")
    
    for iteration in range(max_iterations):
        print(f"\n--- 第 {iteration + 1} 轮迭代 ---")
        
        # 构建分析提示词
        prompt = build_analysis_prompt(context)
        
        # 调用LLM决定下一步操作
        print("正在分析当前状态...")
        response = call_llm(prompt)
        
        if not response:
            print("错误: LLM 调用失败")
            return "抱歉，我无法完成这个任务。"
        
        print(f"LLM 响应: {response}")
        
        # 解析LLM响应
        try:
            decision = json.loads(response)
        except json.JSONDecodeError:
            print("警告: LLM 响应不是有效的JSON格式")
            # 尝试提取JSON部分
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != -1:
                try:
                    decision = json.loads(response[start:end])
                except:
                    return f"无法解析LLM响应: {response}"
            else:
                return f"无法解析LLM响应: {response}"
        
        # 判断是否完成任务
        if decision.get('done', False):
            answer = decision.get('answer', '')
            print(f"\n任务完成！\n最终回答: {answer}")
            return answer
        
        # 继续调用工具
        tool_call = decision.get('tool_call', {})
        tool_name = tool_call.get('name', '')
        arguments = tool_call.get('arguments', {})
        
        if not tool_name:
            return "错误: LLM没有指定要调用的工具"
        
        print(f"\n执行工具: {tool_name}")
        print(f"参数: {arguments}")
        
        # 执行工具
        result = execute_tool(tool_name, arguments)
        print(f"工具执行结果:\n{result}")
        
        # 记录到上下文
        context.add_step(tool_name, arguments, result)
        
        # 尝试从结果中提取有用信息作为变量
        if tool_name == 'search_files':
            # 提取找到的文件列表
            lines = result.split('\n')
            file_list = [line.strip() for line in lines if line.strip() and '\\' in line or '/' in line]
            if file_list:
                context.set_variable('found_files', file_list)
    
    # 达到最大迭代次数
    print(f"\n警告: 已达到最大迭代次数 ({max_iterations})，任务未完成")
    return f"任务未完成，已执行 {max_iterations} 步操作。当前状态:\n{context.get_history_summary()}"

def main():
    """主函数，实现终端聊天界面"""
    # 确保终端使用 UTF-8 编码
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("=== AI 聊天助手（链式工具调用）===")
    print("输入 'exit' 或按 Ctrl+C 退出聊天")
    print("支持的工具：curl_request, list_files, read_file, search_files, create_file")
    print("=" * 60)

    try:
        while True:
            user_input = input("\n你: ")

            if user_input.strip().lower() == 'exit':
                print("再见！")
                break

            print("\n助手: 正在分析请求...")
            result = execute_chained_tool_call(user_input)
            print(f"\n最终结果:\n{result}")

    except KeyboardInterrupt:
        print("\n再见！")

if __name__ == '__main__':
    main()
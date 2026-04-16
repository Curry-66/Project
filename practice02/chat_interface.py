# -*- coding: utf-8 -*-
import os
import json
import http.client
import time
import sys

# 确保终端编码正确
os.system('chcp 65001 >nul')

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

def clean_thinking_content(text):
    """彻底清理思考过程内容（核心修复：先过滤再打印）"""
    # 1. 移除所有思考过程标签
    text = text.replace('<think>', '').replace('</think>', '')
    
    # 2. 定义所有思考相关关键词（覆盖模型所有可能的思考前缀）
    think_keywords = [
        'Thinking Process', 'ThinkingProcess', 'Analyze the Request', 'AnalyzetheRequest', 
        'Interpret', 'Possibility', 'Constraint', 'Goal', 'Respond to', 
        'Drafting the Response', 'Determine the Appropriate Response', 
        'System Instructions', 'Input from user', 'Role', 'Task', 'Final Review', 
        'Final Output Generation', 'Selecting the Best Fit', 'Draft',
        'Determine the Output', 'DeterminetheOutput', 'Constraint CheckList',
        'Confidence Score'
    ]
    
    # 3. 处理连续流式输出：从第一个思考关键词开始，直接截断所有后续内容
    for kw in think_keywords:
        if kw in text:
            text = text.split(kw)[0]
            break  # 找到第一个思考关键词就截断，避免残留
    
    # 4. 移除角色标识
    text = text.replace('用户：', '').replace('助手：', '').replace('User:', '').replace('Assistant:', '')
    
    # 5. 移除多余空格和空行
    text = text.strip()
    return text

def call_llm_with_history(prompt, history, max_tokens=500):
    """使用标准 http 库调用 LLM，只基于当前输入"""
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

    # 🔴 终极强化系统prompt：强制锁死输出格式
    system_prompt = """
你是一个友好的AI助手，必须严格遵守以下所有规则，违反任何一条都视为失败：
1. 绝对禁止输出任何思考过程、分析逻辑、草稿、推理步骤、选项对比、约束说明；
2. 只允许输出最终给用户的回答，内容必须是中文，简洁明了；
3. 禁止出现任何英文思考关键词，如Thinking Process、Analyze、Draft等；
4. 直接回答用户问题，不要任何多余的解释、分析、格式说明；
5. 只输出最终回答，其他内容一律不允许出现。
"""
    full_prompt = f"{system_prompt}\n用户：{prompt}\n助手："

    # 解析 base_url（兼容http/https）
    is_https = False
    if base_url.startswith('http://'):
        base_url = base_url[7:]
    elif base_url.startswith('https://'):
        base_url = base_url[8:]
        is_https = True

    try:
        host, path = base_url.split('/', 1)
        path = '/' + path
    except Exception as e:
        print(f"错误: 解析 URL 失败: {str(e)}")
        return None

    # 准备请求数据
    data = {
        "model": model,
        "prompt": full_prompt,
        "max_tokens": max_tokens,
        "stream": True
    }

    # 兼容http/https连接
    try:
        if is_https:
            conn = http.client.HTTPSConnection(host, timeout=30)
        else:
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

        clean_output = ""
        # 标记是否已经开始思考过程
        in_thinking = False

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
                        
                        # 检查是否包含<think>标签
                        if '<think>' in text:
                            # 只保留<think>标签之前的内容
                            text = text.split('<think>')[0]
                            # 清理并打印保留的内容
                            text = text.strip()
                            if text:
                                print(text, end='', flush=True)
                                clean_output += text
                            # 标记进入思考过程，后续内容全部跳过
                            in_thinking = True
                        elif '</think>' in text:
                            # 跳过</think>标签及之后的内容
                            in_thinking = False
                            continue
                        elif in_thinking:
                            # 如果已经在思考过程中，跳过所有内容
                            continue
                        else:
                            # 检查是否包含思考过程关键词
                            thinking_keywords = ['ThinkingProcess', 'AnalyzetheRequest', 'ConstraintCheckList', 'ConfidenceScore', 'DeterminetheOutput']
                            has_thinking = any(kw in text for kw in thinking_keywords)
                            
                            if has_thinking:
                                # 如果包含思考过程关键词，只保留关键词之前的内容
                                for kw in thinking_keywords:
                                    if kw in text:
                                        text = text.split(kw)[0]
                                        break
                                # 清理并打印保留的内容
                                text = text.strip()
                                if text:
                                    print(text, end='', flush=True)
                                    clean_output += text
                                # 标记进入思考过程，后续内容全部跳过
                                in_thinking = True
                            else:
                                # 如果不包含思考过程关键词，正常处理
                                text = text.strip()
                                if text:
                                    print(text, end='', flush=True)
                                    clean_output += text
                except json.JSONDecodeError:
                    pass

        return clean_output.strip() if clean_output else None
    except Exception as e:
        print(f"错误: {str(e)}")
        return None
    finally:
        conn.close()

def main():
    """主函数，实现终端聊天界面"""
    # 打印欢迎信息
    print("=== AI 聊天助手 ===")
    print("支持终端界面输入聊天内容、流式输出")
    print("输入 'exit' 或按 Ctrl+C 退出聊天")
    print("=" * 60)

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

            # 调用 LLM 获取响应（不使用历史记录）
            assistant_response = call_llm_with_history(user_input, [])

            # 显示完成状态
            if assistant_response:
                print("\n[状态] 回答完成")

    except KeyboardInterrupt:
        print("\n再见！")

if __name__ == '__main__':
    main()
# -*- coding: utf-8 -*-
import os
import sys
import json
import http.client

# 确保终端使用 UTF-8 编码
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def load_env():
    """加载环境变量"""
    env_vars = {}
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

def list_available_skills():
    """读取可用技能列表"""
    skills = []
    project_root = os.path.abspath(os.path.join(os.getcwd(), '..'))
    skills_dir = os.path.join(project_root, '.agents', 'skills')
    
    if not os.path.exists(skills_dir):
        return skills
    
    try:
        for skill_dir in os.listdir(skills_dir):
            skill_path = os.path.join(skills_dir, skill_dir)
            if os.path.isdir(skill_path):
                skill_file = os.path.join(skill_path, 'SKILL.md')
                if os.path.exists(skill_file):
                    try:
                        with open(skill_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if content.startswith('---'):
                                front_matter_end = content.find('---', 3)
                                if front_matter_end != -1:
                                    front_matter = content[3:front_matter_end].strip()
                                    skill_info = {}
                                    for line in front_matter.split('\n'):
                                        line = line.strip()
                                        if ':' in line:
                                            key, value = line.split(':', 1)
                                            key = key.strip()
                                            value = value.strip()
                                            if key == 'name':
                                                skill_info['name'] = value
                                            elif key == 'description':
                                                skill_info['description'] = value
                                    if 'name' in skill_info:
                                        skills.append(skill_info)
                    except Exception as e:
                        print(f"错误: 读取技能文件 {skill_file} 失败: {str(e)}")
    except Exception as e:
        print(f"错误: 读取技能目录失败: {str(e)}")
    
    return skills

def test_notice_skill_without_department():
    """测试不指定部门的通知技能调用"""
    print("测试 1: 不指定部门，要求撰写五一节放假通知")
    print("用户输入: 请撰写一份关于五一节放假的通知")
    
    env_vars = load_env()
    if not env_vars:
        return

    base_url = env_vars.get('BASE_URL')
    model = env_vars.get('MODEL')
    api_key = env_vars.get('API_KEY')

    if not all([base_url, model, api_key]):
        print("错误: 缺少必要的环境变量")
        return

    # 读取可用技能列表
    skills = list_available_skills()
    skills_json = json.dumps({"skills": skills}, ensure_ascii=False)

    # 系统提示词
    system_prompt = f"""你是一个智能助手，可以使用以下工具来执行网络访问：

工具列表：
1. curl_request
   - 功能：使用 curl 访问网页并返回内容
   - 参数：
     - url: 要访问的网页 URL
     - timeout: 超时时间（可选，默认 30 秒）

可用技能：
{skills_json}

当你需要使用某个技能时，请按照以下格式输出：
[技能调用开始]
技能名称
[技能调用结束]

例如：
[技能调用开始]
notice
[技能调用结束]

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

当技能调用完成后，我会返回技能内容，你需要基于技能内容继续与用户对话。"""

    user_input = "请撰写一份关于五一节放假的通知"
    full_prompt = f"{system_prompt}\n\n用户问：{user_input}\n\n助手回答："

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
        "max_tokens": 1000,
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

        print(f"助手输出: {response_text}")
        print()
    except Exception as e:
        print(f"错误: {str(e)}")
    finally:
        conn.close()

def test_notice_skill_with_department():
    """测试指定部门的通知技能调用"""
    print("测试 2: 指定部门为销售部，要求撰写五一节放假通知")
    print("用户输入: 我是销售部的，请撰写一份关于五一节放假的通知")
    
    env_vars = load_env()
    if not env_vars:
        return

    base_url = env_vars.get('BASE_URL')
    model = env_vars.get('MODEL')
    api_key = env_vars.get('API_KEY')

    if not all([base_url, model, api_key]):
        print("错误: 缺少必要的环境变量")
        return

    # 读取可用技能列表
    skills = list_available_skills()
    skills_json = json.dumps({"skills": skills}, ensure_ascii=False)

    # 系统提示词
    system_prompt = f"""你是一个智能助手，可以使用以下工具来执行网络访问：

工具列表：
1. curl_request
   - 功能：使用 curl 访问网页并返回内容
   - 参数：
     - url: 要访问的网页 URL
     - timeout: 超时时间（可选，默认 30 秒）

可用技能：
{skills_json}

当你需要使用某个技能时，请按照以下格式输出：
[技能调用开始]
技能名称
[技能调用结束]

例如：
[技能调用开始]
notice
[技能调用结束]

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

当技能调用完成后，我会返回技能内容，你需要基于技能内容继续与用户对话。"""

    user_input = "我是销售部的，请撰写一份关于五一节放假的通知"
    full_prompt = f"{system_prompt}\n\n用户问：{user_input}\n\n助手回答："

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
        "max_tokens": 1000,
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

        print(f"助手输出: {response_text}")
        print()
    except Exception as e:
        print(f"错误: {str(e)}")
    finally:
        conn.close()

def main():
    """主测试函数"""
    print("=== 技能调用功能测试 ===")
    print()
    
    test_notice_skill_without_department()
    test_notice_skill_with_department()
    
    print("=== 测试完成 ===")

if __name__ == '__main__':
    main()
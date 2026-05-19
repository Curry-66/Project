# -*- coding: utf-8 -*-
import os
import sys
import io

# 添加当前目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_1_file_search(execute_chained_tool_call):
    """测试1：文件搜索链式调用"""
    print("=" * 60)
    print("测试1：文件搜索链式调用")
    print("=" * 60)
    user_request = "请查找 practice02 和 practice05 目录下所有包含'def'关键词的文件，并总结这些文件的主要内容"
    print(f"用户请求: {user_request}")
    print("\n" + "=" * 60 + "\n")
    
    result = execute_chained_tool_call(user_request, max_iterations=5)
    
    print("\n" + "=" * 60)
    print("测试1完成")
    print("=" * 60 + "\n")
    return result

def test_2_skill_query(execute_chained_tool_call):
    """测试2：技能查询链式调用"""
    print("=" * 60)
    print("测试2：技能查询链式调用")
    print("=" * 60)
    user_request = "我想了解 notice 技能的详细规则"
    print(f"用户请求: {user_request}")
    print("\n" + "=" * 60 + "\n")
    
    result = execute_chained_tool_call(user_request, max_iterations=5)
    
    print("\n" + "=" * 60)
    print("测试2完成")
    print("=" * 60 + "\n")
    return result

def test_3_web_page_processing(execute_chained_tool_call):
    """测试3：网页处理链式调用"""
    print("=" * 60)
    print("测试3：网页处理链式调用")
    print("=" * 60)
    user_request = "访问 http://163.com/news/article/KRGTR2H0000189FH.html 并提取页面标题，保存到 output/title.txt"
    print(f"用户请求: {user_request}")
    print("\n" + "=" * 60 + "\n")
    
    result = execute_chained_tool_call(user_request, max_iterations=5)
    
    print("\n" + "=" * 60)
    print("测试3完成")
    print("=" * 60 + "\n")
    return result

def main():
    """主测试函数"""
    # 确保终端使用 UTF-8 编码
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    # 延迟导入，避免 stdout 问题
    from chat_with_chained_calls import execute_chained_tool_call
    
    print("=== 链式工具调用功能测试 ===")
    print()
    
    # 测试1
    test_1_file_search(execute_chained_tool_call)
    
    # 测试2
    test_2_skill_query(execute_chained_tool_call)
    
    # 测试3
    test_3_web_page_processing(execute_chained_tool_call)
    
    print("=== 所有测试完成 ===")

if __name__ == '__main__':
    main()
# -*- coding: utf-8 -*-
import os
import sys
import json

# 确保终端使用 UTF-8 编码
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加当前目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from chat_with_skills import list_available_skills, load_skill_content

def test_list_available_skills():
    """测试读取技能列表"""
    print("测试 1: 读取技能列表")
    skills = list_available_skills()
    print(f"可用技能数量: {len(skills)}")
    for skill in skills:
        print(f"技能名称: {skill.get('name')}, 描述: {skill.get('description')}")
    print()

def test_load_skill_content():
    """测试加载技能内容"""
    print("测试 2: 加载技能内容")
    skill_name = "notice"
    content = load_skill_content(skill_name)
    print(f"技能 {skill_name} 的内容:")
    print(content)
    print()

def test_skill_rules():
    """测试技能规则是否正确"""
    print("测试 3: 检查技能规则")
    skill_name = "notice"
    content = load_skill_content(skill_name)
    
    # 检查规则是否包含关键内容
    rules = [
        "通知不能以\"通知\"二字开头",
        "必须冠以\"XX部\"的前缀",
        "如果用户没有告知所在部门，使用\"XX部\"代替"
    ]
    
    for rule in rules:
        if rule in content:
            print(f"✓ 规则包含: {rule}")
        else:
            print(f"✗ 规则缺失: {rule}")
    print()

def main():
    """主测试函数"""
    print("=== 技能管理功能测试 ===")
    print()
    
    test_list_available_skills()
    test_load_skill_content()
    test_skill_rules()
    
    print("=== 测试完成 ===")

if __name__ == '__main__':
    main()
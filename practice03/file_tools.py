# -*- coding: utf-8 -*-
"""文件操作工具模块"""
import os
import stat
import time

def list_files(directory):
    """列出目录下的所有文件及其属性
    
    Args:
        directory (str): 要列出的目录路径
    
    Returns:
        str: 格式化的文件列表信息
    """
    try:
        # 检查目录是否存在
        if not os.path.exists(directory):
            return f"错误: 目录 '{directory}' 不存在"
        
        if not os.path.isdir(directory):
            return f"错误: '{directory}' 不是一个目录"
        
        # 列出目录内容
        files = []
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            stat_info = os.stat(item_path)
            
            # 获取文件类型
            if os.path.isdir(item_path):
                file_type = "目录"
            elif os.path.isfile(item_path):
                file_type = "文件"
            else:
                file_type = "其他"
            
            # 获取文件大小
            size = stat_info.st_size
            
            # 获取修改时间
            modify_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat_info.st_mtime))
            
            # 获取权限
            permissions = stat.filemode(stat_info.st_mode)
            
            files.append({
                "name": item,
                "type": file_type,
                "size": size,
                "modify_time": modify_time,
                "permissions": permissions
            })
        
        # 格式化输出
        result = f"目录 '{directory}' 中的文件:\n"
        for file_info in files:
            result += f"- 名称: {file_info['name']}\n"
            result += f"  类型: {file_info['type']}\n"
            result += f"  大小: {file_info['size']} 字节\n"
            result += f"  修改时间: {file_info['modify_time']}\n"
            result += f"  权限: {file_info['permissions']}\n"
        
        return result
    except Exception as e:
        return f"错误: {str(e)}"

def rename_file(directory, old_name, new_name):
    """修改目录下文件的名字
    
    Args:
        directory (str): 文件所在目录
        old_name (str): 旧文件名
        new_name (str): 新文件名
    
    Returns:
        str: 操作结果
    """
    try:
        old_path = os.path.join(directory, old_name)
        new_path = os.path.join(directory, new_name)
        
        # 检查旧文件是否存在
        if not os.path.exists(old_path):
            return f"错误: 文件 '{old_path}' 不存在"
        
        # 检查新文件名是否已存在
        if os.path.exists(new_path):
            return f"错误: 文件 '{new_path}' 已存在"
        
        # 执行重命名
        os.rename(old_path, new_path)
        return f"成功: 文件已从 '{old_name}' 重命名为 '{new_name}'"
    except Exception as e:
        return f"错误: {str(e)}"

def delete_file(directory, file_name):
    """删除目录下的文件
    
    Args:
        directory (str): 文件所在目录
        file_name (str): 要删除的文件名
    
    Returns:
        str: 操作结果
    """
    try:
        file_path = os.path.join(directory, file_name)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return f"错误: 文件 '{file_path}' 不存在"
        
        # 执行删除
        os.remove(file_path)
        return f"成功: 文件 '{file_name}' 已删除"
    except Exception as e:
        return f"错误: {str(e)}"

def create_file(directory, file_name, content):
    """在目录下新建文件并写入内容
    
    Args:
        directory (str): 要创建文件的目录
        file_name (str): 文件名
        content (str): 文件内容
    
    Returns:
        str: 操作结果
    """
    try:
        # 检查目录是否存在
        if not os.path.exists(directory):
            return f"错误: 目录 '{directory}' 不存在"
        
        if not os.path.isdir(directory):
            return f"错误: '{directory}' 不是一个目录"
        
        file_path = os.path.join(directory, file_name)
        
        # 检查文件是否已存在
        if os.path.exists(file_path):
            return f"错误: 文件 '{file_path}' 已存在"
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"成功: 文件 '{file_name}' 已创建并写入内容"
    except Exception as e:
        return f"错误: {str(e)}"

def read_file(directory, file_name):
    """读取目录下文件的内容
    
    Args:
        directory (str): 文件所在目录
        file_name (str): 要读取的文件名
    
    Returns:
        str: 文件内容或错误信息
    """
    try:
        file_path = os.path.join(directory, file_name)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return f"错误: 文件 '{file_path}' 不存在"
        
        if not os.path.isfile(file_path):
            return f"错误: '{file_path}' 不是一个文件"
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return f"文件 '{file_name}' 的内容:\n\n{content}"
    except Exception as e:
        return f"错误: {str(e)}"

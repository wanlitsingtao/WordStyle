#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整理根目录文件，将无关文件移动到archive目录
"""
import os
import shutil
from pathlib import Path

def organize_files():
    """整理根目录文件"""
    base_dir = Path('.')
    archive_dir = base_dir / 'archive'
    
    # 确保archive目录存在
    archive_dir.mkdir(exist_ok=True)
    
    # 定义需要移动的文件模式
    patterns_to_archive = {
        '测试文档': ['*.docx'],
        '日志文件': ['*.log', '*.err.log'],
        '临时文件': ['temp_*', 'result_*'],
        '备份文件': ['*-backup*', '*_backup*', '*.bak'],
        '分析脚本': ['analyze_*.py', 'check_*.py', 'debug_*.py', 'find_*.py', 'locate_*.py', 'search_*.py', 'test_*.py', 'verify_*.py', 'compare_*.py', 'simple_*.py', 'quick_*.py'],
        '文档文件': ['*.md', '*.txt'],
        '其他脚本': ['1.*.py', '3.*.py', '5.*.py', '6.*.py', 'two_step_*.py'],
    }
    
    # 保留的关键文件（不移动）
    keep_files = {
        'app.py', 'doc_converter.py', 'doc_converter_gui.py',
        'config.py', 'utils.py', 'user_manager.py', 'comments_manager.py',
        'task_manager.py', 'admin_dashboard.py', 'admin_tool.py', 'admin_web.py',
        '启动Web应用.bat', '启动转换工具.bat',
        'requirements.txt', 'requirements_web.txt',
        'README.md', 'README_WEB.md', '更新日志.md',
        '.gitignore',
    }
    
    moved_count = 0
    
    for pattern_type, patterns in patterns_to_archive.items():
        print(f"\n📁 处理 {pattern_type}...")
        
        for pattern in patterns:
            for file_path in base_dir.glob(pattern):
                # 跳过目录
                if file_path.is_dir():
                    continue
                
                # 跳过保留文件
                if file_path.name in keep_files:
                    print(f"  ⏭️  保留: {file_path.name}")
                    continue
                
                # 跳过已经在archive中的文件
                if 'archive' in str(file_path):
                    continue
                
                # 移动文件
                dest = archive_dir / file_path.name
                
                # 如果目标文件已存在，添加序号
                if dest.exists():
                    counter = 1
                    while dest.exists():
                        stem = file_path.stem
                        suffix = file_path.suffix
                        dest = archive_dir / f"{stem}_{counter}{suffix}"
                        counter += 1
                
                try:
                    shutil.move(str(file_path), str(dest))
                    print(f"  ✅ 移动: {file_path.name} -> archive/")
                    moved_count += 1
                except Exception as e:
                    print(f"  ❌ 失败: {file_path.name} - {e}")
    
    print(f"\n✅ 整理完成！共移动 {moved_count} 个文件到 archive/ 目录")
    print(f"📊 根目录剩余文件数: {len(list(base_dir.iterdir()))}")
    print(f"📊 archive目录文件数: {len(list(archive_dir.iterdir()))}")

if __name__ == '__main__':
    organize_files()

# -*- coding: utf-8 -*-
"""
测试合并单元格检测和警告功能
"""
from doc_converter import DocumentConverter
import os

print("=" * 60)
print("测试合并单元格检测和警告功能")
print("=" * 60)

converter = DocumentConverter()

source_file = "8js3.docx"
template_file = "mb.docx"
output_file = "test_merge_warning_result.docx"

print(f"\n源文件: {source_file}")
print(f"模板文件: {template_file}")
print(f"输出文件: {output_file}")
print(f"\n开始转换...")
print("-" * 60)

# 收集警告信息
warnings = []

def warning_callback(message):
    warnings.append(message)
    print(f"⚠️  {message}")

success, msg = converter.convert_styles(source_file, template_file, output_file, warning_callback=warning_callback)

print("-" * 60)
if success:
    print(f"✅ 转换成功!")
    
    if os.path.exists(output_file):
        file_size = os.path.getsize(output_file)
        print(f"📄 文件大小: {file_size / 1024 / 1024:.2f} MB")
        print(f"📍 文件路径: {os.path.abspath(output_file)}")
        
        # 统计警告
        merge_warnings = [w for w in warnings if "合并单元格" in w]
        print(f"\n📊 合并单元格警告统计:")
        print(f"   总警告数: {len(warnings)}")
        print(f"   合并单元格警告: {len(merge_warnings)}")
        
        if merge_warnings:
            print(f"\n前5个合并单元格警告示例:")
            for i, w in enumerate(merge_warnings[:5], 1):
                print(f"   {i}. {w}")
    else:
        print("❌ 文件未生成")
else:
    print(f"❌ 转换失败: {msg}")

print("\n" + "=" * 60)

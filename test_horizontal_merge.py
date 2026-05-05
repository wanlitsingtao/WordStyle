# -*- coding: utf-8 -*-
"""
测试表格横向合并单元格功能
"""
from doc_converter import DocumentConverter
import os

def test_horizontal_merge():
    """测试横向合并单元格复制"""
    
    # 测试文件路径
    source_file = "E:/LingMa/8js3.docx"  # 使用包含合并单元格的文档
    template_file = "E:/LingMa/mb.docx"
    output_file = "E:/LingMa/test_horizontal_merge_result.docx"
    
    print("=" * 60)
    print("测试表格横向合并单元格功能")
    print("=" * 60)
    
    if not os.path.exists(source_file):
        print(f"❌ 源文件不存在: {source_file}")
        return
    
    if not os.path.exists(template_file):
        print(f"❌ 模板文件不存在: {template_file}")
        return
    
    converter = DocumentConverter()
    
    # 警告回调
    def warning_callback(message):
        print(f"⚠️  警告: {message}")
    
    print(f"\n开始转换...")
    print(f"源文件: {source_file}")
    print(f"模板文件: {template_file}")
    print(f"输出文件: {output_file}\n")
    
    success, msg = converter.convert_styles(
        source_file=source_file,
        template_file=template_file,
        output_file=output_file,
        warning_callback=warning_callback
    )
    
    if success:
        print("✅ 转换成功！")
        print(f"输出文件已保存: {output_file}")
        print("\n请手动检查输出文件中的表格：")
        print("1. 横向合并单元格是否正确保留")
        print("2. 表格样式是否应用了模板样式")
        print("3. 单元格内容是否正确复制")
    else:
        print(f"❌ 转换失败: {msg}")

if __name__ == "__main__":
    test_horizontal_merge()

# -*- coding: utf-8 -*-
"""
测试图片尺寸修复功能
验证转换后的图片是否保持源文档中的原始显示尺寸
"""
from doc_converter import DocumentConverter
import os

def test_image_size_preservation():
    """测试图片尺寸是否正确保留"""
    
    # 配置
    source_file = "E:/LingMa/8js3.docx"
    template_file = "E:/LingMa/mb.docx"
    output_file = "E:/LingMa/8js3_converted_test_image.docx"
    
    if not os.path.exists(source_file):
        print(f"错误：源文件不存在 {source_file}")
        return
    
    if not os.path.exists(template_file):
        print(f"错误：模板文件不存在 {template_file}")
        return
    
    print("=" * 60)
    print("测试图片尺寸修复功能")
    print("=" * 60)
    print(f"源文件: {source_file}")
    print(f"模板文件: {template_file}")
    print(f"输出文件: {output_file}")
    print()
    
    # 创建转换器
    converter = DocumentConverter()
    
    # 执行转换
    print("开始转换...")
    success, msg = converter.convert_styles(
        source_file=source_file,
        template_file=template_file,
        output_file=output_file,
        warning_callback=lambda m: print(f"警告: {m}")
    )
    
    if success:
        print("\n✅ 转换成功！")
        print(f"消息: {msg}")
        print(f"\n输出文件已保存: {output_file}")
        print("\n请手动检查转换后的文档，确认图片尺寸是否与源文档一致。")
    else:
        print("\n❌ 转换失败！")
        print(f"错误: {msg}")

if __name__ == "__main__":
    test_image_size_preservation()

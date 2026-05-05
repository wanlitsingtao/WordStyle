# -*- coding: utf-8 -*-
"""
测试 Visio 图和 OLE 对象转换功能
"""
import os
from doc_converter import DocumentConverter

def test_visio_conversion():
    """测试包含 Visio 图的文档转换"""
    
    # 使用已知的包含 Visio 图的文件
    source_file = "e:\\LingMa\\8js2.docx"
    template_file = "e:\\LingMa\\mb.docx"
    output_file = "e:\\LingMa\\test_visio_output.docx"
    
    if not os.path.exists(source_file):
        print(f"源文件不存在: {source_file}")
        return
    
    if not os.path.exists(template_file):
        print(f"模板文件不存在: {template_file}")
        return
    
    print("开始测试 Visio 图转换...")
    print(f"源文件: {source_file}")
    print(f"模板文件: {template_file}")
    print(f"输出文件: {output_file}")
    print("=" * 60)
    
    converter = DocumentConverter()
    
    try:
        success, message = converter.convert_styles(source_file, template_file, output_file)
        
        if success:
            print("\n✓ 转换成功!")
            print(f"消息: {message}")
            
            # 检查输出文件是否存在
            if os.path.exists(output_file):
                print(f"✓ 输出文件已创建: {output_file}")
                
                # 检查输出文件中是否包含特殊对象
                from docx import Document
                from docx.oxml.ns import qn
                
                output_doc = Document(output_file)
                object_count = 0
                shape_count = 0
                
                for para in output_doc.paragraphs:
                    objects = para._element.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}object')
                    shapes = para._element.findall('.//{urn:schemas-microsoft-com:vml}shape')
                    
                    if objects:
                        object_count += len(objects)
                    
                    if shapes:
                        shape_count += len(shapes)
                
                print(f"\n输出文件中的特殊对象统计:")
                print(f"  - OLE 对象: {object_count}")
                print(f"  - VML 形状: {shape_count}")
                
                if object_count > 0 or shape_count > 0:
                    print("\n✓ Visio 图和 OLE 对象已成功复制到输出文件!")
                else:
                    print("\n⚠ 警告: 输出文件中未检测到特殊对象")
            else:
                print("✗ 输出文件未创建")
        else:
            print(f"\n✗ 转换失败: {message}")
    
    except Exception as e:
        print(f"\n✗ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("测试完成!")

if __name__ == "__main__":
    test_visio_conversion()

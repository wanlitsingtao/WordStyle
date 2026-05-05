# -*- coding: utf-8 -*-
"""
简单测试 Visio 图检测功能
"""
import os
from docx import Document

def simple_test():
    """简单测试"""
    
    source_file = "e:\\LingMa\\8js2.docx"
    
    if not os.path.exists(source_file):
        print(f"源文件不存在: {source_file}")
        return
    
    print("正在分析源文件中的特殊对象...")
    
    try:
        doc = Document(source_file)
        
        object_count = 0
        shape_count = 0
        para_with_objects = 0
        
        for idx, para in enumerate(doc.paragraphs):
            objects = para._element.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}object')
            shapes = para._element.findall('.//{urn:schemas-microsoft-com:vml}shape')
            
            if objects or shapes:
                para_with_objects += 1
                object_count += len(objects)
                shape_count += len(shapes)
                print(f"段落 {idx}: 发现 {len(objects)} 个 OLE 对象, {len(shapes)} 个 VML 形状")
        
        print(f"\n统计结果:")
        print(f"  包含特殊对象的段落数: {para_with_objects}")
        print(f"  OLE 对象总数: {object_count}")
        print(f"  VML 形状总数: {shape_count}")
        
        if object_count > 0 or shape_count > 0:
            print("\n✓ 成功检测到 Visio 图和 OLE 对象!")
        else:
            print("\n⚠ 未检测到特殊对象")
    
    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_test()

# -*- coding: utf-8 -*-
"""
快速测试 Word COM 转换
"""
import os
import sys

try:
    import win32com.client
except ImportError:
    print("错误：未安装 pywin32")
    print("请运行: pip install pywin32")
    sys.exit(1)

def quick_test():
    source_file = "e:\\LingMa\\8js3.docx"
    output_file = "e:\\LingMa\\8js3_quick_test.docx"
    
    if not os.path.exists(source_file):
        print(f"错误：源文件不存在 {source_file}")
        return False
    
    word = None
    doc = None
    
    try:
        print("正在启动 Word...")
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0
        
        print(f"正在打开: {os.path.basename(source_file)}")
        doc = word.Documents.Open(os.path.abspath(source_file))
        
        print(f"正在另存为: {os.path.basename(output_file)}")
        doc.SaveAs(os.path.abspath(output_file))
        
        print("\n✓ 测试成功！")
        print(f"输出文件: {output_file}")
        
        # 检查文件大小
        if os.path.exists(output_file):
            size = os.path.getsize(output_file)
            print(f"文件大小: {size / 1024 / 1024:.2f} MB")
            
            # 检查是否包含 Visio 图
            from docx import Document
            test_doc = Document(output_file)
            object_count = 0
            for para in test_doc.paragraphs:
                objects = para._element.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}object')
                object_count += len(objects)
            
            print(f"Visio 图数量: {object_count}")
            
            if object_count > 0:
                print("\n✓✓✓ 成功！Visio 图已完整复制！")
            else:
                print("\n⚠ 警告：未检测到 Visio 图")
        
        return True
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        try:
            if doc:
                doc.Close(SaveChanges=0)
            if word:
                word.Quit()
        except:
            pass

if __name__ == "__main__":
    print("=" * 60)
    print("Word COM 转换快速测试")
    print("=" * 60)
    print()
    
    success = quick_test()
    
    print("\n" + "=" * 60)
    if success:
        print("测试完成！请检查生成的文件")
    else:
        print("测试失败")
    print("=" * 60)

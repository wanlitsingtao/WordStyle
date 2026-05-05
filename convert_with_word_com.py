# -*- coding: utf-8 -*-
"""
使用 Word COM 自动化复制包含 Visio 图的文档
需要安装 pywin32: pip install pywin32
"""
import os
import sys
import time

try:
    import win32com.client
    from win32com.client import constants
except ImportError:
    print("错误：未安装 pywin32")
    print("请运行: pip install pywin32")
    sys.exit(1)

def convert_with_word_com(source_file, template_file, output_file):
    """
    使用 Word COM 自动化转换文档
    
    这个方法会：
    1. 打开源文档
    2. 复制所有内容（包括 Visio 图）
    3. 粘贴到基于模板的新文档中
    4. 保存为新文件
    """
    
    print("=" * 60)
    print("使用 Word COM 自动化转换文档")
    print("=" * 60)
    
    if not os.path.exists(source_file):
        print(f"错误：源文件不存在 {source_file}")
        return False
    
    if not os.path.exists(template_file):
        print(f"错误：模板文件不存在 {template_file}")
        return False
    
    word = None
    source_doc = None
    target_doc = None
    
    try:
        # 启动 Word 应用程序
        print("\n正在启动 Word...")
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False  # 后台运行
        word.DisplayAlerts = 0  # 不显示警告
        
        # 打开源文档
        print(f"正在打开源文档: {os.path.basename(source_file)}")
        source_doc = word.Documents.Open(os.path.abspath(source_file))
        
        # 基于模板创建新文档
        print(f"正在基于模板创建新文档: {os.path.basename(template_file)}")
        target_doc = word.Documents.Add(os.path.abspath(template_file))
        
        # 选择源文档的所有内容
        print("正在复制源文档内容...")
        source_range = source_doc.Range()
        source_range.Copy()
        
        # 粘贴到目标文档
        print("正在粘贴到目标文档...")
        target_range = target_doc.Range(0, 0)
        target_range.Paste()
        
        # 等待粘贴完成
        time.sleep(2)
        
        # 保存目标文档
        print(f"正在保存: {os.path.basename(output_file)}")
        target_doc.SaveAs(os.path.abspath(output_file))
        
        print("\n✓ 转换成功！")
        print(f"输出文件: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ 转换失败: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # 关闭文档
        try:
            if source_doc:
                source_doc.Close(SaveChanges=0)
            if target_doc:
                target_doc.Close(SaveChanges=0)
            if word:
                word.Quit()
        except:
            pass
        
        print("\nWord 已关闭")

def convert_simple_copy(source_file, output_file):
    """
    简化版：直接另存为（保留所有内容和格式）
    然后手动应用样式
    """
    
    print("=" * 60)
    print("使用 Word COM 简化转换")
    print("=" * 60)
    
    if not os.path.exists(source_file):
        print(f"错误：源文件不存在 {source_file}")
        return False
    
    word = None
    doc = None
    
    try:
        # 启动 Word
        print("\n正在启动 Word...")
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0
        
        # 打开源文档
        print(f"正在打开: {os.path.basename(source_file)}")
        doc = word.Documents.Open(os.path.abspath(source_file))
        
        # 另存为新文件
        print(f"正在保存为: {os.path.basename(output_file)}")
        doc.SaveAs(os.path.abspath(output_file))
        
        print("\n✓ 转换成功！")
        print(f"输出文件: {output_file}")
        print("\n注意：此方法保留了所有内容（包括 Visio 图）")
        print("      但样式可能需要手动调整")
        
        return True
        
    except Exception as e:
        print(f"\n✗ 转换失败: {e}")
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
    # 配置参数
    source_file = "e:\\LingMa\\8js3.docx"
    template_file = "e:\\LingMa\\mb.docx"
    output_file = "e:\\LingMa\\8js3_com_converted.docx"
    
    print("\n请选择转换模式:")
    print("1. 完整转换（复制内容到模板）- 推荐")
    print("2. 简单另存为（保留所有内容）")
    print()
    
    choice = input("请输入选择 (1/2，默认1): ").strip() or "1"
    
    if choice == "1":
        success = convert_with_word_com(source_file, template_file, output_file)
    elif choice == "2":
        success = convert_simple_copy(source_file, output_file)
    else:
        print("无效选择")
        sys.exit(1)
    
    if success:
        print("\n" + "=" * 60)
        print("完成！请检查输出文件")
        print("=" * 60)
    else:
        print("\n转换失败，请检查错误信息")
        sys.exit(1)

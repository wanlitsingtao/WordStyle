# -*- coding: utf-8 -*-
"""
两步转换脚本：先 COM 转换保留 Visio 图，再普通转换应用其他功能
"""
import os
import sys
import time

try:
    import win32com.client
except ImportError:
    print("错误：未安装 pywin32")
    print("请运行: pip install pywin32")
    sys.exit(1)

from doc_converter import DocumentConverter

def two_step_conversion(source_file, template_file, output_file, 
                        do_mood=True, answer_text="应答：本投标人理解并满足要求。",
                        answer_style="应答句", list_bullet="● "):
    """
    两步转换流程
    
    参数:
        source_file: 源文件路径
        template_file: 模板文件路径
        output_file: 最终输出文件路径
        do_mood: 是否进行祈使语气转换
        answer_text: 应答句文本
        answer_style: 应答句样式
        list_bullet: 列表符号
    """
    
    print("=" * 60)
    print("两步转换流程")
    print("=" * 60)
    
    # 生成中间文件名
    base = os.path.splitext(source_file)[0]
    temp_file = f"{base}_temp_com.docx"
    
    word = None
    doc = None
    
    try:
        # ========== 第一步：COM 转换保留 Visio 图 ==========
        print("\n【第一步】使用 Word COM 转换保留 Visio 图...")
        print("-" * 60)
        
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0
        
        print(f"正在打开: {os.path.basename(source_file)}")
        doc = word.Documents.Open(os.path.abspath(source_file))
        
        print(f"正在保存为: {os.path.basename(temp_file)}")
        doc.SaveAs(os.path.abspath(temp_file))
        
        print("✓ 第一步完成！Visio 图已保留")
        
        # 关闭文档
        doc.Close(SaveChanges=0)
        doc = None
        
        # 等待一下
        time.sleep(1)
        
        # ========== 第二步：普通转换应用其他功能 ==========
        print("\n【第二步】使用 python-docx 应用其他转换功能...")
        print("-" * 60)
        
        converter = DocumentConverter()
        
        print(f"正在处理: {os.path.basename(temp_file)}")
        print(f"  - 祈使语气转换: {'是' if do_mood else '否'}")
        print(f"  - 应答句插入: {answer_text}")
        
        success, msg = converter.full_convert(
            source_file=temp_file,
            template_file=template_file,
            output_file=output_file,
            custom_style_map=None,
            do_mood=do_mood,
            answer_text=answer_text,
            answer_style=answer_style,
            list_bullet=list_bullet
        )
        
        if success:
            print(f"\n✓ 第二步完成！")
            print(f"  输出文件: {output_file}")
        else:
            print(f"\n✗ 第二步失败: {msg}")
            return False
        
        # 清理临时文件
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
                print(f"  已删除临时文件: {temp_file}")
        except:
            pass
        
        print("\n" + "=" * 60)
        print("转换完成！")
        print("=" * 60)
        print("\n⚠️ 重要提示：")
        print("  最终文件中 Visio 图位置会显示占位文本")
        print("  请手动从以下文件复制 Visio 图：")
        print(f"  {temp_file} (如果还存在)")
        print("  或者重新运行第一步生成该文件")
        print("\n建议操作：")
        print("  1. 打开最终文件检查样式和文本转换")
        print("  2. 如有需要，手动复制 Visio 图")
        
        return True
        
    except Exception as e:
        print(f"\n✗ 转换失败: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # 确保关闭 Word
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
    output_file = "e:\\LingMa\\8js3_final.docx"
    
    print("\n配置信息:")
    print(f"  源文件: {source_file}")
    print(f"  模板文件: {template_file}")
    print(f"  输出文件: {output_file}")
    print()
    
    choice = input("是否进行祈使语气转换？(y/n，默认y): ").strip().lower() or "y"
    do_mood = (choice == "y")
    
    print("\n开始转换...\n")
    
    success = two_step_conversion(
        source_file=source_file,
        template_file=template_file,
        output_file=output_file,
        do_mood=do_mood
    )
    
    if success:
        print("\n✓✓✓ 全部完成！")
        print(f"\n请检查文件: {output_file}")
    else:
        print("\n✗✗✗ 转换失败")
        sys.exit(1)

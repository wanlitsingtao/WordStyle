"""
测试应答句插入模式：标题后插入
"""
from doc_converter import DocumentConverter
import os

def test_after_heading_mode():
    """测试标题后插入模式"""
    
    converter = DocumentConverter()
    
    # 使用现有的测试文件
    input_file = "8js3.docx"
    output_file = "test_after_heading_result.docx"
    
    if not os.path.exists(input_file):
        print(f"错误：找不到测试文件 {input_file}")
        return
    
    print("=" * 60)
    print("测试：标题后插入应答句")
    print("=" * 60)
    
    # 测试标题后插入模式
    success, actual_file, msg = converter.insert_response_after_headings(
        input_file=input_file,
        output_file=output_file,
        answer_text="【应答】",
        answer_style="应答句",
        mode='after_heading'  # 关键参数：标题后插入
    )
    
    if success:
        print(f"\n✅ 成功！")
        print(f"输出文件：{actual_file}")
        print(f"详细信息：{msg}")
        
        # 统计结果
        from docx import Document
        doc = Document(actual_file)
        
        heading_count = 0
        answer_count = 0
        
        for para in doc.paragraphs:
            if para.style.name.startswith('Heading'):
                heading_count += 1
            elif '应答' in para.text:
                answer_count += 1
        
        print(f"\n统计信息：")
        print(f"  - 标题数量：{heading_count}")
        print(f"  - 应答句数量：{answer_count}")
        
        print(f"\n请打开文档检查：{actual_file}")
        print("重点检查：")
        print("  1. 第一个标题前是否没有应答句")
        print("  2. 后续标题后是否有应答句（如果标题前是正文）")
        print("  3. 文章最后一段后是否有应答句")
        
    else:
        print(f"\n❌ 失败：{msg}")

if __name__ == "__main__":
    test_after_heading_mode()

"""测试 is_heading_paragraph 方法"""
from doc_converter import DocumentConverter
from docx import Document
from docx.oxml.ns import qn

converter = DocumentConverter()
doc = Document("8js3.docx")

print("=" * 80)
print("测试 is_heading_paragraph 方法")
print("=" * 80)

# 查找包含"3.1"的段落
for i, para in enumerate(doc.paragraphs[:50]):
    if "3.1" in para.text and "智慧运行系统" in para.text:
        style_name = para.style.name if para.style else "None"
        
        # 获取样式ID
        p_pr = para._element.find(qn('w:pPr'))
        style_id = None
        if p_pr is not None:
            pStyle = p_pr.find(qn('w:pStyle'))
            if pStyle is not None:
                style_id = pStyle.get(qn('w:val'))
        
        # 测试 is_heading_paragraph
        is_heading = converter.is_heading_paragraph(para._element, doc)
        
        print(f"\n位置 {i}:")
        print(f"  文本: {para.text[:50]}")
        print(f"  样式名称: {style_name}")
        print(f"  样式ID: {style_id}")
        print(f"  is_heading_paragraph: {is_heading}")

"""检查2级标题的样式ID"""
from docx import Document
from docx.oxml.ns import qn

doc = Document("test_after_heading_result.docx")

print("=" * 80)
print("查找包含'3.1'的段落（应该是2级标题）")
print("=" * 80)

for i, para in enumerate(doc.paragraphs[:100]):
    if "3.1" in para.text and "智慧运行系统" in para.text:
        style_name = para.style.name if para.style else "None"
        
        # 获取样式ID
        p_pr = para._element.find(qn('w:pPr'))
        style_id = None
        if p_pr is not None:
            pStyle = p_pr.find(qn('w:pStyle'))
            if pStyle is not None:
                style_id = pStyle.get(qn('w:val'))
        
        # 检查大纲级别
        has_outline = False
        outline_level = 0
        if p_pr is not None:
            outline_elem = p_pr.find(qn('w:outlineLvl'))
            if outline_elem is not None:
                has_outline = True
                outline_level = int(outline_elem.get(qn('w:val'), 0)) + 1
        
        print(f"\n位置 {i}:")
        print(f"  文本: {para.text[:50]}")
        print(f"  样式名称: {style_name}")
        print(f"  样式ID: {style_id}")
        print(f"  有大纲级别: {has_outline}, 级别: {outline_level}")

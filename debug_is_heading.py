"""调试 is_heading_paragraph 方法"""
from docx import Document
from docx.oxml.ns import qn

doc = Document("8js3.docx")

# 查找包含"3.1"的段落
for i, para in enumerate(doc.paragraphs[:50]):
    if "3.1" in para.text and "智慧运行系统" in para.text:
        print(f"位置 {i}: {para.text[:50]}")
        
        # 获取样式ID
        p_pr = para._element.find(qn('w:pPr'))
        style_id = None
        if p_pr is not None:
            pStyle = p_pr.find(qn('w:pStyle'))
            if pStyle is not None:
                style_id = pStyle.get(qn('w:val'))
        
        print(f"  样式ID: {style_id}")
        
        # 尝试通过样式ID获取样式
        if style_id:
            try:
                style = doc.styles[style_id]
                print(f"  样式对象: {style}")
                print(f"  样式名称: {style.name}")
                print(f"  样式名称是否包含heading: {'heading' in style.name.lower()}")
            except Exception as e:
                print(f"  错误: {e}")

"""
查找包含特定关键词的表格
"""
from docx import Document

def find_table_with_keywords(doc_file, keywords):
    """查找包含所有关键词的表格"""
    doc = Document(doc_file)
    
    for idx, table in enumerate(doc.tables, 1):
        # 提取表格中的所有文本
        all_text = ""
        for row in table.rows:
            for cell in row.cells:
                all_text += cell.text + " "
        
        # 检查是否包含所有关键词
        if all(keyword in all_text for keyword in keywords):
            print(f"\n找到表格 #{idx}:")
            print(f"位置: 第 {idx} 个表格")
            print(f"行数: {len(table.rows)}")
            print(f"列数: {len(table.columns)}")
            print(f"\n表头预览:")
            
            # 显示前3行
            for i, row in enumerate(table.rows[:3]):
                row_text = " | ".join([cell.text[:20] for cell in row.cells])
                print(f"  行 {i+1}: {row_text}")
            
            return idx, table
    
    return None, None

# 搜索关键词
keywords = ["接口位置", "至 ISOS FEP", "IBP"]

for doc_file in ["8js1.docx", "8js2.docx", "8js3.docx"]:
    print(f"\n 搜索 {doc_file}...")
    idx, table = find_table_with_keywords(doc_file, keywords)
    if table:
        print(f"\n✅ 在 {doc_file} 中找到目标表格!")
        break

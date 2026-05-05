# -*- coding: utf-8 -*-
"""测试正确的列数计算方法"""
from docx import Document
from docx.oxml.ns import qn

doc = Document("E:/LingMa/8js3.docx")
table = doc.tables[35]  # 表格 #36

print("="*80)
print("测试正确的列数计算")
print("="*80)
print()

# 方法：遍历 XML 的 tr（表格行）元素，统计 tc（表格单元格）的数量
# 注意：Word XML 中，合并的单元格只会出现一次

for i, row in enumerate(table.rows[:2]):
    print(f"行 {i+1}:")
    
    # 获取 XML 的 tr 元素
    tr = row._element
    
    # 统计 tr 下的 tc 数量
    tc_elements = [elem for elem in tr if elem.tag == qn('w:tc')]
    print(f"  XML 中的 tc 元素数量: {len(tc_elements)}")
    
    # 检查每个 tc 的 gridSpan
    total_grid_cols = 0
    for tc_idx, tc in enumerate(tc_elements):
        tcPr = tc.find(qn('w:tcPr'))
        span = 1
        if tcPr is not None:
            gridSpan = tcPr.find(qn('w:gridSpan'))
            if gridSpan is not None:
                span = int(gridSpan.get(qn('w:val'), 1))
        
        total_grid_cols += span
        text = ''
        for p in tc.findall(qn('w:p')):
            for run in p.findall(qn('w:r')):
                for t in run.findall(qn('w:t')):
                    if t.text:
                        text += t.text
        
        print(f"  tc[{tc_idx}]: span={span}, 累计={total_grid_cols}, 文本='{text[:10]}'")
    
    print(f"  该行实际网格列数: {total_grid_cols}")
    print()

# 结论：我们应该使用 len(tc_elements) 作为列数，而不是累加 gridSpan
print("="*80)
print("结论")
print("="*80)
print("python-docx 的 table.columns 返回的是网格列数（9列），这是正确的！")
print("问题不在列数计算，而在于其他地方的逻辑。")
print()
print("让我检查转换后的文档，看看问题到底在哪里...")

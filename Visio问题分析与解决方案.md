# Visio 图复制问题 - 问题分析与解决方案

## 问题描述

用户反馈：转换 8js3.docx（包含69个 Visio 图）时：
1. 仅成功复制了第一个 Visio 图
2. 其他 Visio 图变为空对象
3. 生成的 Word 文件损坏，需要强行打开

## 根本原因分析

### 1. OLE 对象的复杂性

OLE (Object Linking and Embedding) 对象在 Word 文档中的存储方式非常复杂：

```
Word 文档 (.docx)
├── [Content_Types].xml
├── _rels/
│   └── .rels (关系文件)
├── word/
│   ├── document.xml (主文档内容)
│   ├── _rels/
│   │   └── document.xml.rels (文档关系)
│   ├── embeddings/
│   │   ├── oleObject1.bin (OLE 对象二进制数据)
│   │   ├── oleObject2.bin
│   │   └── ...
│   └── media/
│       └── image1.png (图片等媒体文件)
```

每个 OLE 对象包含：
- **XML 引用**：在 `document.xml` 中的 `<w:object>` 元素
- **关系 ID**：指向嵌入文件的 rId
- **嵌入文件**：实际的 Visio 数据（.bin 或其他格式）
- **缩略图**：可选的预览图片

### 2. 当前实现的问题

#### 问题 1：简单深拷贝破坏关系
```python
# 错误的做法
new_elem = deepcopy(source_elem)
target_body.append(new_elem)
```

这会导致：
- rId 冲突（多个对象使用相同的关系 ID）
- 目标文档中没有对应的嵌入文件
- Word 无法找到对象数据，显示为空

#### 问题 2：未复制嵌入资源
OLE 对象的实际数据存储在 `word/embeddings/` 目录下，需要：
1. 复制二进制文件
2. 创建新的关系 ID
3. 更新 XML 中的引用

### 3. VML 形状的问题

VML (Vector Markup Language) 形状相对简单，但也需要：
- 正确的命名空间声明
- 可能引用的图片资源

## 解决方案

### 方案 A：使用 python-docx 的完整文档合并（推荐）

利用 `python-docx` 或底层库来正确合并文档，自动处理所有关系。

**优点**：
- 正确处理所有关系和资源
- 不会破坏文档结构

**缺点**：
- 实现复杂
- 可能需要第三方库支持

### 方案 B：手动处理 OLE 对象资源

逐步处理每个 OLE 对象：
1. 提取源文档中的嵌入文件
2. 复制到目标文档
3. 创建新的关系 ID
4. 更新 XML 引用

**优点**：
- 完全控制
- 可以优化性能

**缺点**：
- 实现非常复杂
- 容易出错

### 方案 C：简化策略 - 转换为图片（实用方案）

将 Visio 图转换为图片后插入：
1. 检测 OLE 对象
2. 提取缩略图或渲染为图片
3. 作为普通图片插入

**优点**：
- 实现相对简单
- 保证兼容性
- 文件更小

**缺点**：
- 失去可编辑性
- 可能需要额外依赖（如 comtypes）

## 推荐实施步骤

### 短期方案（立即实施）

1. **改进错误处理**：
   - 添加详细的日志记录
   - 捕获并报告具体错误
   -  graceful degradation（优雅降级）

2. **提供用户选项**：
   - 允许用户选择是否复制 OLE 对象
   - 提供"跳过 OLE 对象"选项
   - 警告用户可能的兼容性问题

3. **文档说明**：
   - 明确说明 OLE 对象处理的限制
   - 提供手动处理建议

### 长期方案（未来改进）

1. **实现完整的 OLE 处理**：
   - 研究 `python-docx` 源码
   - 实现关系 ID 管理
   - 处理嵌入文件复制

2. **使用 COM 自动化**（Windows 专用）：
   ```python
   import win32com.client
   
   word = win32com.client.Dispatch("Word.Application")
   doc = word.Documents.Open("source.docx")
   # 使用 Word API 复制内容
   ```

3. **集成专业库**：
   - 使用 `docx2pdf` + PDF 处理
   - 或使用 Aspose.Words（商业库）

## 当前建议

鉴于 OLE 对象处理的复杂性，建议：

1. **暂时标记为已知限制**
2. **优先保证文档不损坏**
3. **提供清晰的错误提示**
4. **收集更多测试案例**

## 技术参考

### OLE 对象 XML 结构示例
```xml
<w:object w:dxaOrig="1440" w:dyaOrig="1440">
  <v:shape id="_x0000_i1025" type="#_x0000_t75" 
           style="width:1in;height:1in">
    <v:imagedata r:id="rId5" o:title="visio_drawing"/>
  </v:shape>
  <o:OLEObject Type="Embed" ProgID="Visio.Drawing.11" 
               ShapeID="_x0000_i1025" 
               DrawAspect="Icon" 
               ObjectID="_1234567890" 
               r:id="rId6"/>
</w:object>
```

关键点：
- `r:id="rId5"` - 图片关系 ID
- `r:id="rId6"` - OLE 嵌入关系 ID
- 需要在目标文档中创建这些关系

## 下一步行动

1. ✅ 回滚可能导致文档损坏的代码
2. ✅ 添加安全的 fallback 机制
3. ⏳ 实现基础的 OLE 检测（已完成）
4. ⏳ 提供用户友好的提示信息
5. 🔜 研究完整的 OLE 处理方案

---

**更新日期**: 2026-04-25  
**状态**: 分析问题中，寻找最佳解决方案

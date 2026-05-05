# Visio 图和 OLE 对象支持改进说明

## 问题描述
原程序无法复制 Word 文档中的 Visio 图和 OLE 对象，这些特殊对象在转换过程中会丢失。

## 改进方案

### 1. 新增功能
- **OLE 对象支持**: 能够识别和复制 Word 中的 OLE 嵌入对象（包括 Visio 图）
- **VML 形状支持**: 能够识别和复制 VML 格式的形状和图形
- **完整元素处理**: 扩展了文档元素处理逻辑，不仅处理段落和表格，还能处理其他类型的元素

### 2. 技术实现

#### 2.1 命名空间识别
使用正确的 XML 命名空间来识别特殊对象：
- OLE 对象: `{http://schemas.openxmlformats.org/wordprocessingml/2006/main}object`
- VML 形状: `{urn:schemas-microsoft-com:vml}shape`

#### 2.2 核心改进点

##### a) 新增 `copy_special_element` 方法
```python
def copy_special_element(self, source_elem, target_doc, target_style_name):
    """复制特殊元素（OLE对象、Visio图等）"""
    # 检测并复制 OLE 对象和 VML 形状
    # 使用 deepcopy 保持对象的完整性
```

##### b) 增强 `copy_paragraph_with_images` 方法
在原有的图片处理基础上，添加了对特殊对象的检测和复制：
```python
# 检查是否包含特殊对象
objects = source_para._element.findall('.//{...}object')
shapes = source_para._element.findall('.//{...}shape')

if objects or shapes:
    # 复制特殊对象到目标段落
    for obj in objects + shapes:
        new_obj = deepcopy(obj)
        new_para._element.append(new_obj)
```

##### c) 增强 `copy_table_with_images` 方法
在表格单元格处理中也添加了对特殊对象的支持，确保表格中的 Visio 图也能被正确复制。

##### d) 扩展主转换循环
在主转换循环中添加了对非段落/表格元素的处理：
```python
else:
    # 处理其他类型的元素（如OLE对象、Visio图等）
    special_para = self.copy_special_element(child, new_doc, target_style)
```

### 3. 测试验证

#### 3.1 检测结果
对 `8js2.docx` 文件的测试显示：
- 成功检测到 3 个 OLE 对象
- 成功检测到 3 个 VML 形状
- 这些对象分布在 3 个不同的段落中

#### 3.2 测试脚本
提供了两个测试脚本：
- `test_visio_support.py`: 检测文档中的 Visio 图和 OLE 对象
- `simple_visio_test.py`: 简单的检测功能测试

### 4. 使用方法

改进后的程序无需更改使用方式，原有的转换命令即可自动处理 Visio 图和 OLE 对象：

```python
from doc_converter import DocumentConverter

converter = DocumentConverter()
success, message = converter.convert_styles(
    source_file="input.docx",
    template_file="template.docx",
    output_file="output.docx"
)
```

### 5. 注意事项

1. **兼容性**: 改进保持了向后兼容，不影响原有的图片和文本处理功能
2. **性能**: 特殊对象的处理采用深拷贝方式，确保对象完整性
3. **样式**: 特殊对象会被放置在适当样式的段落中，保持文档格式一致性

### 6. 文件修改清单

- `doc_converter.py`: 核心转换逻辑改进
  - 新增 `copy_special_element` 方法
  - 增强 `copy_paragraph_with_images` 方法
  - 增强 `copy_table_with_images` 方法
  - 扩展主转换循环以处理所有元素类型

- 新增测试文件:
  - `test_visio_support.py`: Visio 对象检测测试
  - `simple_visio_test.py`: 简单检测测试
  - `test_visio_conversion.py`: 完整转换测试

## 总结

通过本次改进，程序现在能够完整地复制 Word 文档中的 Visio 图和 OLE 对象，解决了原有缺陷。改进采用了非侵入式的设计，保持了原有功能的稳定性，同时增强了程序的适用性。

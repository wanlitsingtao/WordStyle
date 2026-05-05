# Visio 图和 OLE 对象处理 - 用户指南

## 快速开始

### 1. 检测文档中的 Visio 图

运行以下命令检测您的 Word 文档中是否包含 Visio 图或 OLE 对象：

```bash
python simple_visio_test.py
```

修改脚本中的 `source_file` 变量指向您要检查的文件。

### 2. 转换包含 Visio 图的文档

使用原有的转换方式即可，程序会自动处理 Visio 图：

#### 方法一：使用命令行
```bash
python doc_converter.py your_document.docx -t template.docx
```

#### 方法二：使用 GUI
```bash
python doc_converter_gui.py
```

#### 方法三：在代码中使用
```python
from doc_converter import DocumentConverter

converter = DocumentConverter()
success, message = converter.convert_styles(
    source_file="input.docx",
    template_file="template.docx",
    output_file="output.docx"
)

if success:
    print("转换成功！")
else:
    print(f"转换失败: {message}")
```

## 支持的 Visio 图类型

程序现在支持以下类型的嵌入对象：

1. **OLE 对象** (Object Linking and Embedding)
   - Microsoft Visio 绘图
   - Excel 图表
   - PowerPoint 幻灯片
   - 其他 OLE 嵌入对象

2. **VML 形状** (Vector Markup Language)
   - Visio 图形
   - 流程图
   - 组织结构图
   - 其他 VML 格式的形状

## 常见问题

### Q1: 如何确认我的文档包含 Visio 图？
运行 `simple_visio_test.py` 脚本，它会告诉您文档中包含多少个 OLE 对象和 VML 形状。

### Q2: 转换后 Visio 图会保持可编辑吗？
是的，OLE 对象会以原始格式复制，在 Word 中双击仍可编辑（需要安装相应的应用程序，如 Visio）。

### Q3: Visio 图的位置会改变吗？
程序会尽量保持 Visio 图在原文档中的位置，但由于样式转换，可能会有细微的位置调整。

### Q4: 如果转换失败怎么办？
1. 检查源文件和模板文件是否存在
2. 确保文件没有被其他程序占用
3. 查看错误日志文件（通常以 `_err.log` 结尾）
4. 尝试使用简化版的测试脚本定位问题

### Q5: 大型文档转换很慢怎么办？
包含大量 Visio 图的文档转换时间会增加，这是正常的。建议在后台运行转换任务。

## 技术细节

### XML 命名空间
程序使用以下命名空间来识别特殊对象：
- OLE 对象: `http://schemas.openxmlformats.org/wordprocessingml/2006/main`
- VML 形状: `urn:schemas-microsoft-com:vml`

### 复制机制
- 使用深拷贝 (deepcopy) 确保对象完整性
- 保留所有对象的属性和关系
- 自动处理对象相关的资源和引用

## 示例

### 示例 1: 检测特定文件
```python
# 修改 simple_visio_test.py 中的文件路径
source_file = "e:\\LingMa\\your_document.docx"
```

### 示例 2: 批量处理
```python
import os
from doc_converter import DocumentConverter

converter = DocumentConverter()
template = "template.docx"

for filename in os.listdir("input_folder"):
    if filename.endswith(".docx"):
        source = os.path.join("input_folder", filename)
        output = os.path.join("output_folder", filename)
        
        success, msg = converter.convert_styles(source, template, output)
        print(f"{filename}: {'成功' if success else '失败'}")
```

## 性能优化建议

1. **关闭其他程序**: 转换时关闭 Word 和其他 Office 应用
2. **分批处理**: 对于大量文件，建议分批处理
3. **使用 SSD**: 在固态硬盘上运行可提高速度
4. **充足内存**: 确保系统有足够的可用内存

## 故障排除

### 问题: 转换后 Visio 图显示为空白
**解决方案**: 
- 确保目标计算机安装了 Visio 或相应的查看器
- 检查 OLE 对象是否正确嵌入

### 问题: 转换过程中程序卡住
**解决方案**:
- 检查文件大小，超大文件可能需要更多时间
- 查看是否有文件被锁定
- 尝试重启程序

### 问题: 某些 Visio 图丢失
**解决方案**:
- 运行检测脚本确认源文件中确实包含这些对象
- 检查对象是否以其他格式嵌入
- 联系技术支持获取帮助

## 更新日志

### v1.4 (当前版本)
- ✓ 新增 OLE 对象支持
- ✓ 新增 VML 形状支持
- ✓ 扩展元素处理逻辑
- ✓ 改进对象复制机制
- ✓ 添加检测工具

## 获取帮助

如果您遇到问题：
1. 查看 `Visio支持改进说明.md` 了解技术细节
2. 运行测试脚本验证功能
3. 检查错误日志文件
4. 联系技术支持

---

**注意**: 本改进完全向后兼容，不影响原有功能。您可以安全地升级并使用新功能。

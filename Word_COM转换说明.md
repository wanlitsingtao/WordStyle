# Word COM 自动化转换 - 完整复制 Visio 图

## 📋 说明

这个脚本使用 **Word COM 自动化**来转换文档，可以**完整复制 Visio 图和所有 OLE 对象**。

## ⚙️ 前置要求

### 1. 安装 pywin32

```bash
pip install pywin32
```

### 2. 系统要求

- ✅ Windows 操作系统
- ✅ 已安装 Microsoft Word
- ✅ Python 3.x

## 🚀 使用方法

### 方法 1：直接运行

```bash
python convert_with_word_com.py
```

程序会提示您选择转换模式：
- **模式 1**：完整转换（推荐）- 复制内容到模板
- **模式 2**：简单另存为 - 保留所有内容但样式需手动调整

### 方法 2：在代码中使用

```python
from convert_with_word_com import convert_with_word_com

success = convert_with_word_com(
    source_file="8js3.docx",
    template_file="mb.docx",
    output_file="output.docx"
)

if success:
    print("转换成功！")
```

## 📊 两种模式对比

| 特性 | 模式 1：完整转换 | 模式 2：简单另存为 |
|------|-----------------|-------------------|
| Visio 图复制 | ✓ 完整复制 | ✓ 完整复制 |
| 样式应用 | ✓ 自动应用模板样式 | ✗ 需手动调整 |
| 文本格式 | ✓ 保持 | ✓ 保持 |
| 表格 | ✓ 保持 | ✓ 保持 |
| 处理速度 | 较慢（约 1-2 分钟） | 快速（几秒） |
| 适用场景 | 需要应用模板样式 | 只需保留内容 |

## 💡 推荐工作流程

### 对于 8js3.docx（69个 Visio 图）

#### 步骤 1：使用 COM 转换
```bash
python convert_with_word_com.py
# 选择模式 1
```

#### 步骤 2：验证结果
- 打开生成的 `8js3_com_converted.docx`
- 确认所有 Visio 图都已正确复制
- 检查样式是否正确应用

#### 步骤 3：如需进一步处理
如果需要祈使语气转换或插入应答句，可以：
```bash
python doc_converter.py 8js3_com_converted.docx -t mb.docx
```

## ⚠️ 注意事项

1. **Word 会在后台运行**
   - 转换过程中会启动 Word（不可见）
   - 转换完成后会自动关闭
   - 如果程序异常退出，可能需要手动关闭 Word 进程

2. **首次运行可能较慢**
   - Word 启动需要时间
   - 大文件复制可能需要 1-2 分钟

3. **确保 Word 未被占用**
   - 转换前关闭所有 Word 文档
   - 避免同时运行多个转换任务

## 🔧 故障排除

### 问题 1：ImportError: No module named 'win32com'

**解决方案**：
```bash
pip install pywin32
```

### 问题 2：Word 无法启动

**解决方案**：
- 确认已安装 Microsoft Word
- 尝试以管理员身份运行
- 检查 Word 是否正常启动

### 问题 3：转换后 Word 进程未关闭

**解决方案**：
打开任务管理器，结束 `WINWORD.EXE` 进程

### 问题 4：权限错误

**解决方案**：
- 以管理员身份运行命令提示符
- 确保对文件有读写权限

## 📝 自定义参数

修改脚本底部的配置：

```python
if __name__ == "__main__":
    source_file = "e:\\LingMa\\your_source.docx"
    template_file = "e:\\LingMa\\your_template.docx"
    output_file = "e:\\LingMa\\your_output.docx"
```

## 🎯 优势

与之前的 python-docx 方案相比：

| 特性 | python-docx | Word COM |
|------|-------------|----------|
| Visio 图复制 | ✗ 不支持 | ✓ 完整支持 |
| OLE 对象 | ✗ 不支持 | ✓ 完整支持 |
| 文档完整性 | ⚠️ 可能损坏 | ✓ 保证完整 |
| 样式控制 | ✓ 精细控制 | ⚠️ 依赖 Word |
| 跨平台 | ✓ 是 | ✗ 仅 Windows |
| 速度 | 快 | 较慢 |
| 依赖 | python-docx | Word + pywin32 |

## 📞 需要帮助？

如果遇到问题：
1. 检查是否安装了 pywin32
2. 确认 Word 可以正常启动
3. 查看错误信息
4. 尝试重启计算机

---

**创建日期**: 2026-04-25  
**版本**: 1.0  
**平台**: Windows only

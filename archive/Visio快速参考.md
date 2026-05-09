# Visio 图支持 - 快速参考

## 🎯 改进内容
✅ 现在程序可以复制 Word 文档中的 **Visio 图** 和 **OLE 对象**

## 🚀 快速使用

### 检测 Visio 图
```bash
python simple_visio_test.py
```

### 转换文档（自动处理 Visio 图）
```bash
python doc_converter.py input.docx -t template.docx
```

或使用 GUI:
```bash
python doc_converter_gui.py
```

## 📋 支持的对象类型

| 类型 | 说明 | 示例 |
|------|------|------|
| OLE 对象 | 嵌入的外部对象 | Visio 图、Excel 图表、PPT 幻灯片 |
| VML 形状 | 矢量图形 | 流程图、组织结构图、示意图 |

## 🔍 如何确认文档包含 Visio 图？

运行检测脚本后会显示：
```
段落 XXX: 发现 X 个 OLE 对象, X 个 VML 形状
```

如果数字 > 0，说明文档包含 Visio 图或 OLE 对象。

## 💡 重要提示

1. **无需更改使用方法** - 程序会自动处理
2. **保持可编辑性** - 转换后的 Visio 图仍可双击编辑
3. **需要相应软件** - 编辑 Visio 图需要安装 Visio

## 📁 相关文件

- `doc_converter.py` - 核心转换程序（已改进）
- `simple_visio_test.py` - 快速检测工具
- `Visio处理用户指南.md` - 详细使用说明
- `Visio支持改进说明.md` - 技术文档

## ❓ 常见问题

**Q: 转换后 Visio 图会丢失吗？**  
A: 不会，现在会完整复制。

**Q: 需要安装 Visio 才能查看吗？**  
A: 查看不需要，但编辑需要。

**Q: 会影响转换速度吗？**  
A: 轻微影响，通常在可接受范围内。

**Q: 旧版本转换的文档怎么办？**  
A: 重新运行转换即可，新版本会正确处理 Visio 图。

## 📞 需要帮助？

1. 查看 `Visio处理用户指南.md`
2. 运行测试脚本验证功能
3. 检查错误日志文件

---
**版本**: v1.4 | **日期**: 2026-04-25

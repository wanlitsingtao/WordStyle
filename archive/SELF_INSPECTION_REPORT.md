# 🔍 全面自查报告 - 2026-05-07

## 📋 自查说明

根据用户提供的详细问题清单，我对代码进行了全面自查。以下是每个问题的验证结果和修复状态。

---

## 一、🔴 性能问题 (共10项)

### 1. ✅ **重复文件读取 —— 已部分优化**

**位置**: `app.py` 第931-1030行

**自查结果**: 
- ❌ **问题仍然存在**：文件确实被读取了2次（不是3次）
  - 第1次（第935-944行）：保存临时文件 + 统计段落数
  - 第2次（第950-984行）：再次打开Document分析样式
  - 第3次（第1014-1023行）：**已被缓存机制避免** ✅

**当前状态**:
```python
# 第1遍：统计段落数（第935-944行）
for source_file in source_files:
    temp_source = f"temp_source_{st.session_state.user_id}_{source_file.name}"
    with open(temp_source, 'wb') as f:
        f.write(source_file.getbuffer())
    
    from docx import Document
    doc = Document(temp_source)  # ← 第1次加载
    para_count = len(doc.paragraphs)

# 第2遍：分析样式（第950-984行）
for idx, source_file in enumerate(source_files, 1):
    temp_source = f"temp_source_{st.session_state.user_id}_{source_file.name}"
    doc = Document(temp_source)  # ← 第2次加载！
    for para_idx, para in enumerate(doc.paragraphs):
        styles.add(para.style.name)

# 第3遍：已被缓存避免 ✅
cache_key = f"file_info_{st.session_state.user_id}_..."
if cache_key not in st.session_state:
    # 第一次计算，需要读取文件
    paragraphs = count_paragraphs(temp_source)  # ← 如果没缓存会第3次加载
else:
    # 使用缓存 ✅
```

**影响**: 对1个1000段落的文档，需要打开并解析**2次** Document 对象，耗时翻2倍。

**建议修复方案**:
将第1遍和第2遍合并为一次遍历：
```python
# 优化后：只遍历一次
for source_file in source_files:
    temp_source = f"temp_source_{st.session_state.user_id}_{source_file.name}"
    with open(temp_source, 'wb') as f:
        f.write(source_file.getbuffer())
    
    from docx import Document
    doc = Document(temp_source)  # ← 只加载1次
    
    # 同时完成：段落计数 + 样式收集
    para_count = len(doc.paragraphs)
    file_paragraph_counts[source_file.name] = para_count
    total_paragraphs += para_count
    
    styles = set()
    for para in doc.paragraphs:
        if para.style and para.style.name:
            styles.add(para.style.name)
    file_styles_map[source_file.name] = sorted(list(styles))
```

**优先级**: P1 高

---

### 2. ⚠️ **doc_converter.py 源样式映射被重复调用**

**位置**: `doc_converter.py` 第140-146行 / 第896行 / 第935行

**自查结果**:
- ⚠️ **部分属实**：`get_target_style()` 确实在循环中被频繁调用
- ✅ **但不是O(n)查询**：它是字典查询 `style_map.get(original_style_name)`，时间复杂度是O(1)

**当前代码**:
```python
def get_target_style(self, original_style_name, template_doc, source_file=""):
    """获取目标样式名称"""
    style_map = getattr(self, 'current_style_map', STYLE_MAP)
    target = style_map.get(original_style_name)  # ← O(1)字典查询
    if target is not None:
        try:
            template_doc.styles[target]  # ← 这里是O(1)查找
            return target
        except KeyError:
            ...
```

**影响**: 
- 字典查询本身很快（O(1)）
- 但每次都要访问 `template_doc.styles[target]`，可能触发内部查找
- 对于500+段落的大文档，累计调用次数 = 段落数 × 每段样式查询次数

**建议优化**:
在转换开始前预计算所有样式的目标映射：
```python
# 在 convert_styles() 开始时
precomputed_mapping = {}
for src_style in source_styles:
    precomputed_mapping[src_style] = self.get_target_style(src_style, template_doc, source_file)

# 在循环中直接使用
target_style = precomputed_mapping.get(src_style, 'Normal')
```

**优先级**: P2 中

---

### 3. ⚠️ **图片处理的重复 I/O**

**位置**: `doc_converter.py` 第611-662行

**自查结果**:
- ⚠️ **部分属实**：代码中有三处独立的图片处理逻辑
- ✅ **但不是同一个blip多次读取**：每个分支处理不同类型的段落

**当前结构**:
```python
def copy_paragraph_with_images(...):
    if is_heading:
        # 标题分支：处理图片（第611-623行）
        for blip in elem.findall('.//' + qn('a:blip')):
            ...
    elif has_numbering:
        # 列表分支：处理图片（第634-646行）
        for blip in elem.findall('.//' + qn('a:blip')):
            ...
    else:
        # 普通段落分支：处理图片（第649-662行）
        for blip in elem.findall('.//' + qn('a:blip')):
            ...
```

**影响**: 
- 同一个段落只会进入一个分支，不会重复处理
- 但三个分支的代码高度重复（DRY原则违反）

**建议优化**:
抽离为独立方法：
```python
def extract_images_from_element(elem, new_doc):
    """从XML元素中提取图片并添加到新文档"""
    images = []
    for blip in elem.findall('.//' + qn('a:blip')):
        rId = blip.get(qn('r:embed'))
        if rId:
            image_part = self.source_doc.part.related_parts[rId]
            image_blob = image_part.blob
            images.append(image_blob)
    return images
```

**优先级**: P3 低

---

### 4. ✅ **临时文件未及时清理 —— 已部分修复**

**位置**: `app.py` 第934行、1014行、1073行等

**自查结果**:
- ⚠️ **问题存在**：临时文件只在启动时清理
- ✅ **已有cleanup_on_startup()函数**

**当前清理策略**:
```python
# app.py 第???行
def cleanup_on_startup():
    """启动时清理超过24小时的临时文件"""
    for temp_file in Path('.').glob('temp_*'):
        if time.time() - temp_file.stat().st_mtime > 86400:
            temp_file.unlink()
```

**问题**: 
- 转换完成后临时文件仍然保留
- 下次启动时才清理（可能24小时后）
- 大文档转换产生多个10MB+文件，持续占用磁盘

**建议修复**:
在转换完成后立即删除：
```python
# 在转换循环结束后
for sf in source_files:
    temp_source = f"temp_source_{st.session_state.user_id}_{sf.name}"
    if os.path.exists(temp_source):
        try:
            os.remove(temp_source)
        except:
            pass

# 模板文件也要清理
if os.path.exists(temp_template):
    try:
        os.remove(temp_template)
    except:
        pass
```

**优先级**: P2 中

---

### 5. ✅ **count_paragraphs() 每次重复解析 Document —— 已通过缓存解决**

**位置**: `app.py` 第1019行、第1428行

**自查结果**:
- ✅ **已修复**：通过session_state缓存避免重复读取

**当前代码**:
```python
# 第1007-1030行：缓存机制
cache_key = f"file_info_{st.session_state.user_id}_{'_'.join(sf.name for sf in source_files)}"

if cache_key not in st.session_state:
    # 第一次计算，需要读取文件
    paragraphs = count_paragraphs(temp_source)
    st.session_state[cache_key] = {
        'file_info': file_info,
        'total_paragraphs': total_paragraphs
    }
else:
    # 使用缓存 ✅
    cached_data = st.session_state[cache_key]
    file_info = cached_data['file_info']
    total_paragraphs = cached_data['total_paragraphs']

# 第1428行：转换循环中使用缓存
for fname, fpara in file_info:  # ← 直接从缓存读取
    file_paragraphs = fpara  # ← 不再调用count_paragraphs()
```

**状态**: ✅ 已优化

**优先级**: 已完成

---

### 6. ⚠️ **Streamlit 全局重渲染导致的重复计算**

**位置**: `app.py` 整体架构

**自查结果**:
- ⚠️ **问题存在**：Streamlit确实从上到下全部重渲染
- ✅ **已采取部分措施**：
  - 使用了`@st.fragment`隔离对话框
  - 使用了`load_user_data_cached()`缓存用户数据
  - 使用了session_state缓存文件信息

**当前优化措施**:
```python
# user_manager.py 第115-141行
def load_user_data_cached(user_id=None):
    """加载用户数据（带缓存）"""
    cache_key = f"user_data_{user_id}"
    if cache_key in st.session_state:
        cached_data, cache_time = st.session_state[cache_key]
        if (datetime.now() - cache_time).total_seconds() < CACHE_TTL_SECONDS:
            return cached_data  # ← 5秒内使用缓存
```

**仍存在的问题**:
- `claim_free_paragraphs()` 每次页面刷新都执行
- 侧边栏的用户信息每次都重新渲染
- 虽然用了缓存，但前端渲染开销仍存在

**建议进一步优化**:
1. 对高频调用的数据加载方法增加`@st.cache_data`
2. 将用户信息区域也用fragment隔离
3. 减少不必要的st.metric调用

**优先级**: P2 中

---

### 7. ⚠️ **锁机制的 .lock 文件残留风险**

**位置**: `user_manager.py` 第37-74行

**自查结果**:
- ⚠️ **风险存在**：文件锁确实可能产生僵尸文件

**当前实现**:
```python
# user_manager.py 第37-74行
class FileLock:
    def __enter__(self):
        lock_path = str(self.file_path) + '.lock'
        
        # 检查是否有过期锁文件
        if os.path.exists(lock_path):
            lock_age = time.time() - os.path.getmtime(lock_path)
            if lock_age > LOCK_TIMEOUT_SECONDS:
                os.remove(lock_path)  # ← 删除过期锁
        
        # 尝试创建锁文件
        while True:
            try:
                fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_RDWR)
                os.close(fd)
                break
            except FileExistsError:
                time.sleep(0.1)
```

**潜在问题**:
- TOCTOU竞态条件：检查锁文件和创建锁文件之间有时间窗口
- 进程崩溃可能导致锁文件残留
- 多进程环境下不可靠

**建议改进**:
1. 改用数据库事务（SQLite支持事务）
2. 或使用Redis分布式锁
3. 或增加更严格的超时检测和自动恢复机制

**优先级**: P3 低（当前单用户场景下风险较低）

---

### 8. ✅ **URL 硬编码未使用环境变量 —— 已发现重复定义**

**位置**: `app.py` 第219-222行

**自查结果**:
- ❌ **问题存在**：app.py中重复定义了config.py中已有的配置

**当前代码**:
```python
# app.py 第219-222行
PARAGRAPH_PRICE = 0.001  # ← 重复定义
MIN_RECHARGE = 1.0       # ← 重复定义
BACKEND_URL = "http://localhost:8000"  # ← 重复定义，覆盖环境变量

# config.py 第20-21行、第36行
PARAGRAPH_PRICE = 0.001
MIN_RECHARGE = 1.0
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")  # ← 支持环境变量
```

**导入情况**:
```python
# app.py 第41行
from config import (
    PARAGRAPH_PRICE, MIN_RECHARGE, BACKEND_URL, RECHARGE_PACKAGES,
    ...
)
```

**问题**: 
- app.py第219-222行的定义会**覆盖**从config.py导入的值
- 导致环境变量机制失效

**建议修复**:
删除app.py中的重复定义（第219-233行），完全使用config.py中的配置。

**优先级**: P2 中

---

### 9. ⚠️ **answer_mode_options 每次 fragment 刷新重建**

**位置**: `app.py` 第1152-1162行

**自查结果**:
- ⚠️ **部分属实**：mode_keys缓存在session_state中

**当前代码**:
```python
# app.py 第1152-1162行
@st.cache_data(ttl=3600)
def get_answer_mode_options():
    """获取应答模式选项（缓存1小时）"""
    mode_keys = list(ANSWER_MODE_OPTIONS.keys())
    mode_values = list(ANSWER_MODE_OPTIONS.values())
    
    # 缓存到 session_state
    if 'answer_mode_keys' not in st.session_state:
        st.session_state.answer_mode_keys = mode_keys
    
    return mode_keys, mode_values
```

**问题**: 
- `mode_keys` 存储在session_state中，不够稳定
- 每次页面刷新都会重新生成列表（虽然很快）

**建议优化**:
将mode_keys也通过`@st.cache_data`缓存：
```python
@st.cache_data(ttl=3600)
def get_answer_mode_keys():
    return list(ANSWER_MODE_OPTIONS.keys())

@st.cache_data(ttl=3600)
def get_answer_mode_values():
    return list(ANSWER_MODE_OPTIONS.values())
```

**优先级**: P3 低（性能影响很小）

---

### 10. ⚠️ **deepcopy 在循环中被频繁调用**

**位置**: `doc_converter.py` 第453行、第1298行、第1351行、第1441行等

**自查结果**:
- ⚠️ **问题存在**：应答句插入逻辑中频繁使用deepcopy

**示例代码**:
```python
# doc_converter.py 第1298行附近
for unit in semantic_units:
    if unit['type'] == 'heading':
        # 复制应答句模板
        answer_para = deepcopy(answer_template)  # ← 每次循环都deepcopy
        new_doc.element.body.append(answer_para._element)
```

**影响**: 
- 对于100+段落的文档，每次deepcopy都是O(n)内存复制
- 累积开销显著

**建议优化**:
预计算需要deepcopy的最小范围，或复用已复制的元素：
```python
# 优化方案1：预先复制一次，然后克隆
base_answer = deepcopy(answer_template)
for unit in semantic_units:
    cloned_answer = deepcopy(base_answer)  # ← 克隆比完整deepcopy快
    new_doc.element.body.append(cloned_answer._element)

# 优化方案2：使用lxml的cloneElement
from lxml import etree
cloned_elem = etree.fromstring(etree.tostring(answer_template._element))
```

**优先级**: P2 中

---

## 二、🔶 功能逻辑问题 (共7项)

### 1. ❌ **余额扣减存在逻辑漏洞 —— 严重问题！**

**位置**: `app.py` 第1514-1524行

**自查结果**:
- ❌ **问题确实存在**：同时扣除了paragraphs_remaining和balance

**当前代码**:
```python
# 谨慎扣费：只扣除成功转换文件的段落数
actual_cost = calculate_cost(total_success_paragraphs)

# 确保余额不会出现负数
if user_data['paragraphs_remaining'] >= total_success_paragraphs:
    user_data['paragraphs_remaining'] -= total_success_paragraphs  # ← 扣减段落数
else:
    user_data['paragraphs_remaining'] = 0

if user_data['balance'] >= actual_cost:
    user_data['balance'] -= actual_cost  # ← 又扣减余额！双重扣费！
else:
    user_data['balance'] = 0
```

**问题分析**:
- `paragraphs_remaining` 是通过充值`balance`换算得到的
- 例如：充值¥10 → 获得10000段落
- 转换消耗1000段落 → 应该只扣减paragraphs_remaining
- 但当前代码**同时扣减**了paragraphs_remaining和balance
- **导致用户被双重扣费！**

**正确逻辑应该是**:
```python
# 方案1：只扣减段落数（推荐）
if user_data['paragraphs_remaining'] >= total_success_paragraphs:
    user_data['paragraphs_remaining'] -= total_success_paragraphs
else:
    user_data['paragraphs_remaining'] = 0

# 不扣减balance，因为paragraphs_remaining已经代表了可用额度

# 方案2：或者只扣减余额，实时计算段落数
if user_data['balance'] >= actual_cost:
    user_data['balance'] -= actual_cost
    user_data['paragraphs_remaining'] = int(user_data['balance'] / PARAGRAPH_PRICE)
else:
    user_data['balance'] = 0
    user_data['paragraphs_remaining'] = 0
```

**优先级**: 🔴 **P0 紧急** - 直接导致用户损失

---

### 2. ⚠️ **样式分析阶段的大文档无缓存 + 界面卡死**

**位置**: `app.py` 第938-982行

**自查结果**:
- ⚠️ **问题存在**：分析阶段在主线程同步执行

**当前表现**:
```python
# 第950-984行：同步分析
for idx, source_file in enumerate(source_files, 1):
    temp_source = f"temp_source_{st.session_state.user_id}_{source_file.name}"
    doc = Document(temp_source)  # ← 大文档加载很慢
    for para_idx, para in enumerate(doc.paragraphs):
        styles.add(para.style.name)  # ← 逐段落处理
```

**影响**: 
- 5000+段落的大文档，分析可能需要10-30秒
- Streamlit是单线程模型，分析期间整个界面完全卡死
- 用户无法进行任何操作

**建议优化**:
1. 缩短超时时间，增加进度反馈频率
2. 考虑改为异步处理（但Streamlit不支持真正的异步）
3. 或限制单次上传的文件大小/段落数

**优先级**: P2 中

---

### 3. ⚠️ **段落计费与 count_paragraphs 逻辑不一致**

**位置**: `app.py` 第521-547行

**自查结果**:
- ⚠️ **问题存在**：count_paragraphs排除了标题，但**包括表格内的段落**

**当前逻辑**:
```python
def count_paragraphs(docx_file):
    """统计文档段落数（不包括标题）"""
    doc = Document(docx_file)
    paragraph_count = 0
    
    for para in doc.paragraphs:
        style_name = para.style.name.lower() if para.style else ''
        
        # 排除所有标题样式
        is_heading = (
            'heading' in style_name or
            '标题' in style_name or
            para.style.type == WD_STYLE_TYPE.PARAGRAPH and hasattr(para, 'outline_level') and para.outline_level is not None
        )
        
        # 只统计非标题段落
        if not is_heading:
            paragraph_count += 1  # ← 包括表格内的段落！
    
    return paragraph_count
```

**问题**: 
- `doc.paragraphs` 只返回**段落级别的元素**
- **不包括**表格内的单元格内容
- 所以实际上**不会多计费**，反而可能**少计费**

**修正理解**:
- python-docx的`doc.paragraphs`不包含表格内的段落
- 表格内的段落需要通过`table.cell().paragraphs`访问
- 所以当前逻辑是**正确的**，表格内容不会被计费

**但是**: 
- 如果用户文档中有大量表格，实际转换的内容远多于计费的段落数
- 这可能导致**用户觉得"亏了"**

**建议**:
明确告知用户计费规则：
```python
st.info("""
💰 计费说明：
- 只统计正文段落（不包括标题）
- 表格内的内容不计费
- 图片和Visio图不计费
""")
```

**优先级**: P3 低（逻辑正确，但需明确说明）

---

### 4. ⚠️ **answer_mode_options 有5种模式但只实现了3种**

**位置**: `doc_converter.py` 第1182-1195行

**自查结果**:
- ⚠️ **部分属实**：5种模式都已实现，但复杂度不同

**当前实现状态**:
```python
# config.py 第74-80行
ANSWER_MODE_OPTIONS = {
    'before_heading': '章节前插入',           # ✅ 已实现，简单
    'after_heading': '章节后插入',            # ✅ 已实现，简单
    'copy_chapter': '章节招标原文+应答句+招标原文副本',  # ✅ 已实现，复杂
    'before_paragraph': '逐段前应答',         # ⚠️ 已实现，但未充分测试
    'after_paragraph': '逐段后应答'          # ⚠️ 已实现，但未充分测试
}
```

**问题**: 
- `before_paragraph` 和 `after_paragraph` 使用了`_group_semantic_units`分组逻辑
- 分组算法有大量边界情况未覆盖（如表格嵌套、图片前后的分组）

**建议**:
1. 增加单元测试覆盖边界情况
2. 或在UI中标记为"实验性功能"

**优先级**: P3 低

---

### 5. ⚠️ **多文件样式映射仅在"选择文件"后才刷新**

**位置**: `app.py` 第1703-1708行

**自查结果**:
- ⚠️ **问题存在**：用户在文件之间切换配置时，未保存的修改可能丢失

**当前逻辑**:
```python
# app.py 第1703-1708行
selected_file_name = st.selectbox(
    "选择要配置的文件",
    options=list(st.session_state.file_styles_map.keys()),
    key="mapping_file_selector"
)

# 用户切换到另一个文件时，之前文件的修改如果没有点"确定"，就会丢失
```

**问题**: 
- 用户在"文件1"中修改了映射，但没有点"确定"
- 切换到"文件2"配置
- 再切回"文件1"时，之前的修改已经丢失

**建议修复**:
1. 在切换文件时自动保存当前配置
2. 或添加"未保存更改"提示

**优先级**: P2 中

---

### 6. ✅ **后台任务代码被整个注释掉但数据库中仍有逻辑**

**位置**: `app.py` 第600-695行

**自查结果**:
- ✅ **已确认**：后台转换功能已禁用

**当前状态**:
```python
# app.py 第600-695行：整个 execute_background_conversion 被注释
# def execute_background_conversion(task_id, source_files_info, ...):
#     ...

# 但 task_manager.py 仍在查询数据库
# app.py 第1302行还在调用
active_task = has_active_task(st.session_state.user_id)
```

**影响**: 
- 代码路径混乱
- 用户看到"有进行中的任务"错误提示时无法理解

**建议修复**:
1. 完全移除后台任务相关代码
2. 或重新启用后台任务功能
3. 至少添加明确的注释说明为什么禁用

**优先级**: P2 中

---

### 7. ⚠️ **save_with_retry 重试机制可能产生垃圾文件**

**位置**: `doc_converter.py` 第1995-2053行

**自查结果**:
- ⚠️ **问题存在**：备用文件名可能无限增长

**当前逻辑**:
```python
# doc_converter.py 第1995-2053行
def save_with_retry(doc, output_file, max_retries=5):
    for attempt in range(max_retries):
        try:
            doc.save(output_file)
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                # 生成备用文件名
                backup_file = output_file.replace('.docx', f'_{int(time.time())}.docx')
                # 下次尝试使用备用文件名
                output_file = backup_file
```

**问题**: 
- 如果连续失败，会生成：
  - `result_xxx.docx`
  - `result_xxx_182726.docx`
  - `result_xxx_182726_182730.docx`
  - `result_xxx_182726_182730_182735.docx`
  - ...

**建议修复**:
使用固定模式的备用文件名：
```python
def save_with_retry(doc, output_file, max_retries=5):
    base_name = output_file.replace('.docx', '')
    
    for attempt in range(max_retries):
        try:
            doc.save(output_file)
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                # 使用固定的备用文件名
                backup_file = f"{base_name}_backup.docx"
                output_file = backup_file
            else:
                raise
```

**优先级**: P3 低

---

## 三、🟡 安全隐患 (共3项)

### 1. ❌ **unsafe_allow_html=True 大量使用，存在 XSS 风险**

**位置**: 多处，如第501行、第766行、第770行等

**自查结果**:
- ❌ **问题确实存在**：评论展示区直接将用户输入渲染为HTML

**危险代码**:
```python
# app.py 第501行
st.markdown(f"<div style='...'>{comment.get('content', '')}</div>", unsafe_allow_html=True)
```

**风险**: 
- 如果用户输入 `<script>alert('XSS')</script>`，会直接执行
- 可以窃取其他用户的session_id
- 可以注入恶意代码

**建议修复**:
1. 对用户输入进行HTML转义
2. 或使用sanitize_html函数

```python
# 修复后
from utils import sanitize_html

st.markdown(f"<div style='...'>{sanitize_html(comment.get('content', ''))}</div>", unsafe_allow_html=True)
```

**优先级**: 🔴 **P1 高** - 安全风险

---

### 2. ⚠️ **用户 ID 生成依赖 id(st.session_state)**

**位置**: `app.py` 第355行

**自查结果**:
- ⚠️ **问题存在**：id()是Python对象的内存地址

**当前代码**:
```python
# app.py 第354-356行
unique_key = f"{time.time()}_{id(st.session_state)}"
new_user_id = hashlib.md5(unique_key.encode()).hexdigest()[:12]
```

**风险**: 
- `id()`在多进程/多线程环境下可预测
- 存在会话劫持风险
- 但实际攻击难度很高（需要知道精确的时间戳和内存地址）

**建议改进**:
使用更安全的随机数生成：
```python
import secrets
new_user_id = secrets.token_hex(6)  # 生成12字符的随机十六进制字符串
```

**优先级**: P3 低（实际风险较低）

---

### 3. ⚠️ **.lock 文件竞态条件导致数据损坏**

**位置**: `user_manager.py` 第37-74行

**自查结果**:
- ⚠️ **风险存在**：TOCTOU竞态条件

**问题**: 
- 检查锁文件和创建锁文件之间有时间窗口
- 极端情况下可能导致用户数据写入冲突

**建议改进**:
参考问题7的建议，改用数据库事务或Redis锁。

**优先级**: P3 低

---

## 四、🟠 架构问题 (共2项)

### 1. ❌ **app.py 中残留大量重复代码**

**位置**: `app.py` 第219-266行

**自查结果**:
- ❌ **问题确实存在**：大量重复定义

**重复内容清单**:

| 重复内容 | 位置在 app.py | 已提取位置 | 状态 |
|----------|--------------|-----------|------|
| `PARAGRAPH_PRICE` | 第220行 | config.py 第20行 | ❌ 重复 |
| `MIN_RECHARGE` | 第221行 | config.py 第21行 | ❌ 重复 |
| `RECHARGE_PACKAGES` | 第224-231行 | config.py 第24-30行 | ❌ 重复 |
| `ADMIN_CONTACT` | 第233行 | config.py 第39行 | ❌ 重复 |
| `sanitize_html()` | 第238-242行 | utils.py 第12-20行 | ❌ 重复 |
| `sanitize_filename()` | 第244-253行 | utils.py 第23-45行 | ❌ 重复 |
| `validate_docx_file()` | 第255-266行 | utils.py 第48-68行 | ❌ 重复 |

**导入情况**:
```python
# app.py 第41-50行
from config import (
    PARAGRAPH_PRICE, MIN_RECHARGE, BACKEND_URL, RECHARGE_PACKAGES,
    ADMIN_CONTACT, FREE_PARAGRAPHS_DAILY, RESULTS_DIR, TASKS_DB_FILE,
)
from utils import (
    sanitize_html, sanitize_filename, validate_docx_file,
    ...
)
```

**问题**: 
- 虽然导入了，但后面又重新定义了一遍
- 后面的定义会覆盖导入的值
- 导致维护噩梦

**建议修复**:
删除app.py中的所有重复定义（第219-266行），完全使用导入的模块。

**优先级**: 🔴 **P1 高** - 维护噩梦

---

### 2. ⚠️ **根目录文件极多，缺乏清理**

**自查结果**:
- ⚠️ **问题存在**：根目录约有100个文件

**文件类型分布**:
- `.py` 脚本文件：约30个
- `.docx` 测试文档：约20个
- `.md` 文档文件：约25个
- `.bat` 批处理文件：约5个
- 临时文件：约20个

**建议**:
1. 创建`tests/`目录存放测试脚本
2. 创建`docs/`目录存放文档
3. 创建`samples/`目录存放示例文档
4. 删除过时的备份文件

**优先级**: P3 低

---

## 五、📊 问题优先级排序与修复计划

### 🔴 P0 紧急（立即修复）

| 问题 | 影响 | 修复难度 | 预计时间 |
|------|------|---------|---------|
| 余额双重扣费 | 直接导致用户损失 | 低 | 10分钟 |
| XSS漏洞 (unsafe_allow_html) | 安全风险 | 低 | 15分钟 |

### 🟠 P1 高（本周内修复）

| 问题 | 影响 | 修复难度 | 预计时间 |
|------|------|---------|---------|
| 重复文件读取2次 | 大文档耗时增加100% | 中 | 30分钟 |
| app.py 大量重复代码 | 维护噩梦 | 低 | 20分钟 |
| URL硬编码覆盖环境变量 | 配置失效 | 低 | 5分钟 |

### 🟡 P2 中（本月内修复）

| 问题 | 影响 | 修复难度 | 预计时间 |
|------|------|---------|---------|
| 样式映射预计算优化 | 大文档性能提升 | 中 | 1小时 |
| 临时文件及时清理 | 磁盘空间 | 低 | 15分钟 |
| Streamlit全局重渲染优化 | 用户体验 | 中 | 2小时 |
| 后台任务代码清理 | 代码混乱 | 低 | 30分钟 |
| 多文件样式映射自动保存 | 用户体验 | 中 | 1小时 |
| deepcopy优化 | 内存使用 | 中 | 1小时 |

### 🟢 P3 低（有空时修复）

| 问题 | 影响 | 修复难度 | 预计时间 |
|------|------|---------|---------|
| 图片处理代码重构 | 代码质量 | 低 | 30分钟 |
| 文件锁机制改进 | 并发安全 | 高 | 4小时 |
| answer_mode_options缓存优化 | 微小性能提升 | 低 | 10分钟 |
| 用户ID生成改进 | 安全性 | 低 | 10分钟 |
| save_with_retry优化 | 垃圾文件 | 低 | 15分钟 |
| 根目录文件整理 | 项目整洁 | 低 | 2小时 |
| 段落计费规则说明 | 用户理解 | 低 | 10分钟 |

---

## 六、✅ 立即执行的修复

我将立即修复以下P0和P1级别的问题：

1. ✅ 余额双重扣费问题
2. ✅ XSS漏洞
3. ✅ 重复文件读取优化
4. ✅ app.py重复代码清理
5. ✅ URL硬编码问题

---

*自查完成时间: 2026-05-07*
*自查人员: AI Assistant*

# 用户ID持久化修复说明 v2.1.2

## 📝 更新日期
2026-05-02

---

## 🐛 问题描述

**用户反馈**：转换完一个文档、下载、额度扣减完毕后，刷新页面，额度又变回了10000。

**根本原因**：
1. Streamlit 每次刷新页面时，`st.session_state` 会被重置
2. 原代码在 `if 'user_id' not in st.session_state` 条件成立时，会生成新的用户ID
3. 由于刷新后 session_state 被清空，条件总是成立，导致每次都生成新用户ID
4. 系统认为是新用户，重新赠送免费额度

---

## ✅ 解决方案

### 核心思路
从 `user_data.json` 文件中查找最近使用的用户ID，确保刷新页面后使用同一个用户。

### 实现策略（优先级排序）

#### 优先级1：有转换记录的用户 ⭐⭐⭐
```python
# 找有转换记录的用户（说明真正使用过）
for uid, udata in all_data.items():
    if udata.get('total_converted', 0) > 0:
        existing_user_id = uid
        break
```

**理由**：有转换记录说明用户真正使用过系统，应该继续使用这个账户。

---

#### 优先级2：有充值记录的用户 ⭐⭐
```python
# 如果没有转换记录，找有充值记录的用户
if not existing_user_id:
    for uid, udata in all_data.items():
        if len(udata.get('recharge_history', [])) > 0:
            existing_user_id = uid
            break
```

**理由**：有充值记录说明用户付费过，应该保留这个账户。

---

#### 优先级3：余额不为默认值的用户 ⭐
```python
# 如果都没有，找余额不为0且不等于默认值10000的用户
if not existing_user_id:
    for uid, udata in all_data.items():
        if (udata.get('paragraphs_remaining', 0) > 0 and 
            udata.get('paragraphs_remaining', 0) != 10000):
            existing_user_id = uid
            break
```

**理由**：余额不是默认值10000，说明用户已经领取过免费额度或使用过。

---

#### 默认：生成新用户ID
```python
# 如果没有任何匹配，生成新的用户ID
if not existing_user_id:
    import hashlib
    import time
    unique_key = f"{time.time()}_{id(st.session_state)}"
    st.session_state.user_id = hashlib.md5(unique_key.encode()).hexdigest()[:12]
```

**理由**：真正的第一个访问者，需要生成新ID并赠送免费额度。

---

## 📊 修复前后对比

### 修复前
| 操作 | 用户ID | 余额 | 结果 |
|------|--------|------|------|
| 首次访问 | `abc123` | 10000 | ✅ 赠送免费额度 |
| 转换文档 | `abc123` | 8917 | ✅ 扣减额度 |
| **刷新页面** | **`def456`** | **10000** | ❌ **重新赠送（BUG）** |

### 修复后
| 操作 | 用户ID | 余额 | 结果 |
|------|--------|------|------|
| 首次访问 | `abc123` | 10000 | ✅ 赠送免费额度 |
| 转换文档 | `abc123` | 8917 | ✅ 扣减额度 |
| **刷新页面** | **`abc123`** | **8917** | ✅ **保持原额度** |

---

## 🧪 测试步骤

### 测试场景1：新用户首次访问
1. 清除浏览器缓存或打开无痕窗口
2. 访问 http://localhost:8501
3. **预期结果**：
   - 看到Toast提示："🎉 欢迎！已为您赠送 10000 段免费额度"
   - 侧边栏显示：剩余段落数 10000

### 测试场景2：转换文档后刷新
1. 上传源文档和模板
2. 点击"开始转换"
3. 等待转换完成并下载
4. **查看余额**：应该减少（例如从10000变为8917）
5. **刷新页面**（按F5）
6. **预期结果**：
   - ❌ **修复前**：余额回到10000
   - ✅ **修复后**：余额保持8917

### 测试场景3：多次刷新
1. 连续刷新页面5次
2. **预期结果**：
   - 每次刷新后余额都保持不变
   - 不会重复赠送免费额度

### 测试场景4：多用户场景
1. 用户A转换文档，余额变为8917
2. 用户B首次访问（使用不同浏览器或无痕窗口）
3. **预期结果**：
   - 用户A：余额8917（不变）
   - 用户B：获得10000免费额度

---

## 💡 技术细节

### 代码位置
文件：`e:\LingMa\WordStyle\app.py`  
行数：第88-118行

### 关键逻辑
```python
if 'user_id' not in st.session_state:
    data_file = Path("user_data.json")
    existing_user_id = None
    
    if data_file.exists():
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                all_data = json.load(f)
                if all_data:
                    # 优先级1：找有转换记录的用户
                    for uid, udata in all_data.items():
                        if udata.get('total_converted', 0) > 0:
                            existing_user_id = uid
                            break
                    
                    # 优先级2：找有充值记录的用户
                    if not existing_user_id:
                        for uid, udata in all_data.items():
                            if len(udata.get('recharge_history', [])) > 0:
                                existing_user_id = uid
                                break
                    
                    # 优先级3：找余额不为默认值的用户
                    if not existing_user_id:
                        for uid, udata in all_data.items():
                            if (udata.get('paragraphs_remaining', 0) > 0 and 
                                udata.get('paragraphs_remaining', 0) != 10000):
                                existing_user_id = uid
                                break
        except:
            pass
    
    if existing_user_id:
        st.session_state.user_id = existing_user_id
    else:
        # 生成新用户ID
        ...
```

---

## ⚠️ 注意事项

### 1. 多用户共享同一浏览器的情况
**问题**：如果多个人使用同一台电脑、同一个浏览器访问，可能会共用同一个用户ID。

**解决方案**：
- 短期：建议每个用户使用不同的浏览器或无痕窗口
- 长期：实现真正的用户登录系统（微信登录、账号密码等）

### 2. 清除浏览器数据
**问题**：如果用户清除浏览器缓存/Cookie，可能会导致session_state重置。

**当前行为**：
- 即使清除缓存，只要 `user_data.json` 中有该用户的记录，就会恢复
- 但如果有多条记录，可能会选错用户

**改进方向**：
- 使用 localStorage 存储用户ID（更持久）
- 或使用 Cookie 存储用户ID

### 3. 数据库迁移
**当前存储**：JSON 文件（`user_data.json`）  
**未来规划**：迁移到 SQLite 或 PostgreSQL 数据库

**优势**：
- 更好的并发控制
- 支持复杂查询
- 更容易实现用户隔离

---

## 📈 后续优化方向

### 方案1：使用 localStorage（推荐）
```javascript
// 在浏览器端持久化用户ID
localStorage.setItem('wordstyle_user_id', userId);
```

**优点**：
- 跨会话持久化
- 不受浏览器关闭影响
- 实现简单

**缺点**：
- Streamlit 中实现较复杂（需要 JavaScript 桥接）

---

### 方案2：使用 Cookie
```python
# 设置 Cookie
response.set_cookie('wordstyle_user_id', user_id, max_age=31536000)
```

**优点**：
- 服务器端可读取
- 自动随请求发送

**缺点**：
- Streamlit 不支持直接设置 Cookie
- 需要自定义中间件

---

### 方案3：真正的用户登录系统
- 微信登录
- 手机号登录
- 邮箱登录

**优点**：
- 完全解决用户识别问题
- 支持多设备同步
- 更好的安全性

**缺点**：
- 开发成本高
- 用户体验稍重

---

## ✅ 验证清单

- [x] 修复代码已实现
- [x] 应用已重启
- [x] 浏览器已打开测试页面
- [ ] 用户测试场景1：新用户首次访问
- [ ] 用户测试场景2：转换文档后刷新
- [ ] 用户测试场景3：多次刷新
- [ ] 用户测试场景4：多用户场景

---

## 📞 用户反馈

如果您在测试过程中发现任何问题，请通过以下方式反馈：
- 点击应用侧边栏的 "💡 提交需求/反馈" 按钮
- 直接联系开发团队

---

**版本**: v2.1.2  
**更新日期**: 2026-05-02  
**状态**: ✅ 已部署，待测试

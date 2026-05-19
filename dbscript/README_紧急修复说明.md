# 数据库紧急修复操作指南

**问题**: users表缺少conversion_history字段，导致API返回500错误  
**根本原因**: alembic_version表被错误标记，导致迁移脚本被跳过  
**修复时间**: 2026-05-17

---

## 🎯 问题症状

### 用户页面
```
获取用户ID失败
用户服务暂时不可用，请稍后刷新页面重试
```

### 管理页面
```
数据加载诊断
数据源模式: api
用户数量: 0
未找到用户数据
API 状态码: 500
```

### Render日志
```
psycopg2.errors.UndefinedColumn: column users.conversion_history does not exist
```

---

## 🔍 根本原因分析

### 问题链条

```
第1次部署（带stamp的旧代码）
  ↓
执行 command.stamp(alembic_cfg, "head")
  ↓
alembic_version表被标记为"最新版本"
  ↓
但实际只执行了部分迁移（到旧链末尾）
  ↓
第2次部署（移除stamp的新代码）
  ↓
command.upgrade()检查alembic_version
  ↓
发现已是"最新版本" → 跳过所有迁移
  ↓
数据库中仍缺少conversion_history等字段
  ↓
models.py查询该字段时报UndefinedColumn错误
  ↓
所有user相关API返回500错误
```

---

## ✅ 修复方案（推荐）

### 方案A：执行SQL修复脚本（推荐）⭐

#### 步骤1：在Supabase中执行修复脚本

1. 登录 [Supabase Dashboard](https://supabase.com/dashboard)
2. 选择您的项目
3. 进入 **SQL Editor**
4. 点击 **New Query**
5. 复制并粘贴以下文件内容：
   ```
   E:\LingMa\WordStyle\dbscript\emergency_fix_20260517.sql
   ```
6. 点击 **Run** 执行脚本

#### 步骤2：重启Render后端服务

1. 登录 [Render Dashboard](https://dashboard.render.com)
2. 找到 `wstest-backend` 服务（或 `wordstyle-backend`）
3. 点击右上角的 **Restart** 按钮
4. 等待服务重新启动（约2-3分钟）

#### 步骤3：验证修复效果

1. 访问用户页面，确认能正常获取用户ID
2. 访问管理页面，确认能正常加载数据
3. 检查Render日志，确认没有500错误

---

### 方案B：手动执行SQL命令（备选）

如果不想使用完整脚本，可以手动执行以下SQL：

```sql
-- 1. 清空alembic_version表
DELETE FROM alembic_version;

-- 2. 添加缺失的字段
ALTER TABLE users ADD COLUMN IF NOT EXISTS conversion_history JSONB DEFAULT '[]'::jsonb;
ALTER TABLE users ADD COLUMN IF NOT EXISTS device_fingerprint VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_claim_date TIMESTAMPTZ;
ALTER TABLE conversion_tasks ADD COLUMN IF NOT EXISTS paragraphs INTEGER DEFAULT 0;

-- 3. 重启Render服务
```

然后在Render Dashboard重启服务。

---

### 方案C：通过Render Shell执行（高级）

1. 在Render Dashboard找到后端服务
2. 进入 **Shell** 标签
3. 执行以下命令：

```bash
# 连接数据库并重置alembic_version
python3 -c "
from sqlalchemy import create_engine, text
import os
url = os.environ['DATABASE_URL'].replace('%', '%%')
engine = create_engine(url)
with engine.connect() as conn:
    conn.execute(text('DELETE FROM alembic_version'))
    conn.commit()
    print('✅ 已重置 alembic_version 表')
"

# 添加缺失字段
python3 -c "
from sqlalchemy import create_engine, text
import os
url = os.environ['DATABASE_URL'].replace('%', '%%')
engine = create_engine(url)
with engine.connect() as conn:
    conn.execute(text('''
        ALTER TABLE users ADD COLUMN IF NOT EXISTS conversion_history JSONB DEFAULT '[]'::jsonb;
        ALTER TABLE users ADD COLUMN IF NOT EXISTS device_fingerprint VARCHAR(255);
        ALTER TABLE users ADD COLUMN IF NOT EXISTS last_claim_date TIMESTAMPTZ;
        ALTER TABLE conversion_tasks ADD COLUMN IF NOT EXISTS paragraphs INTEGER DEFAULT 0;
    '''))
    conn.commit()
    print('✅ 已添加缺失字段')
"
```

4. 重启服务

---

## 📋 修复脚本说明

### emergency_fix_20260517.sql 功能

1. **检查当前状态**
   - 显示alembic_version表的当前版本
   - 检查users表和conversion_tasks表的字段完整性

2. **重置alembic_version**
   - 清空alembic_version表
   - 让下次启动时重新执行所有迁移

3. **手动添加缺失字段**（作为保险）
   - users.conversion_history (JSONB)
   - users.device_fingerprint (VARCHAR)
   - users.last_claim_date (TIMESTAMPTZ)
   - conversion_tasks.paragraphs (INTEGER)

4. **验证修复结果**
   - 显示修复后的表结构
   - 统计记录数
   - 确认alembic_version已清空

---

## ⚠️ 注意事项

### 执行前
- ✅ 建议先备份数据库（Supabase有自动备份）
- ✅ 确保在正确的数据库中执行
- ✅ 确认使用的是SERVICE ROLE密钥（有足够权限）

### 执行后
- ✅ 必须重启Render服务才能生效
- ✅ 检查日志确认迁移正常执行
- ✅ 测试所有功能是否正常

### 常见问题

**Q: 执行脚本后仍然报错？**  
A: 确保已经重启了Render服务，旧的进程还在运行。

**Q: 是否需要重新部署代码？**  
A: 不需要，代码已经是最新的，只需要重启服务。

**Q: 会不会丢失现有数据？**  
A: 不会，脚本只是添加新字段，不会删除或修改现有数据。

---

## 🔄 后续预防

### 避免类似问题再次发生

1. **永远不要在main.py中使用stamp**
   ```python
   # ❌ 错误做法
   command.stamp(alembic_cfg, "head")
   command.upgrade(alembic_cfg, "head")
   
   # ✅ 正确做法
   command.upgrade(alembic_cfg, "head")
   ```

2. **确保迁移脚本格式正确**
   ```python
   # ❌ 错误：使用完整文件名
   down_revision = '20260530_120000_add_conversion_history_to_users'
   
   # ✅ 正确：只使用revision ID
   down_revision = '20260530_120000'
   ```

3. **部署前检查迁移链**
   ```bash
   cd backend
   alembic history  # 查看迁移历史
   alembic current  # 查看当前版本
   ```

4. **监控部署日志**
   - 检查是否有迁移执行日志
   - 确认没有"skipping migration"警告

---

## 📞 联系支持

如果遇到问题，请提供：
1. Supabase SQL Editor的执行结果截图
2. Render服务的完整启动日志
3. 浏览器控制台的错误信息

---

**文档生成时间**: 2026-05-17  
**相关文件**: 
- `dbscript/emergency_fix_20260517.sql`
- `backend/alembic/versions/*.py`
- `backend/app/main.py`

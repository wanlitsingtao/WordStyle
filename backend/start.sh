#!/bin/bash
# 启动脚本 - 处理Alembic迁移并启动应用

echo "🚀 开始启动WordStyle Backend..."

# 尝试stamp当前版本（如果数据库已有记录）
echo "📝 标记当前Alembic版本..."
alembic stamp head 2>/dev/null || echo "⚠️ Stamp失败，继续执行upgrade..."

# 执行数据库迁移
echo "🔄 执行数据库迁移..."
alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ 数据库迁移成功"
else
    echo "❌ 数据库迁移失败，退出"
    exit 1
fi

# 启动FastAPI应用
echo "🌐 启动FastAPI应用..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT

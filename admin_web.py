# -*- coding: utf-8 -*-
"""
WordStyle Pro - Web管理后台
基于PostgreSQL数据库的完整管理系统
"""
import streamlit as st
import sys
import os
from datetime import datetime, timedelta
from typing import Optional

# 添加backend路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.database import engine, get_db
from app.models import User, ConversionTask, Order, SystemConfig
from sqlalchemy import text, func, desc
from sqlalchemy.orm import Session

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="WordStyle Pro - 管理后台",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 样式优化 ====================
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .metric-value {
        font-size: 2.5em;
        font-weight: bold;
    }
    .metric-label {
        font-size: 1em;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 辅助函数 ====================

def get_db_session():
    """获取数据库会话"""
    return Session(engine)

def format_datetime(dt):
    """格式化日期时间"""
    if dt:
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    return '-'

def format_currency(amount):
    """格式化金额"""
    return f"¥{amount:,.2f}" if amount else "¥0.00"

# ==================== 数据看板 ====================

def show_dashboard():
    """显示数据看板"""
    st.title("📊 数据看板")
    st.markdown("---")
    
    db = get_db_session()
    
    try:
        # 获取统计数据
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        
        today = datetime.now().date()
        today_users = db.query(User).filter(
            func.date(User.created_at) == today
        ).count()
        
        total_tasks = db.query(ConversionTask).count()
        completed_tasks = db.query(ConversionTask).filter(
            ConversionTask.status == 'COMPLETED'
        ).count()
        processing_tasks = db.query(ConversionTask).filter(
            ConversionTask.status == 'PROCESSING'
        ).count()
        pending_tasks = db.query(ConversionTask).filter(
            ConversionTask.status == 'PENDING'
        ).count()
        failed_tasks = db.query(ConversionTask).filter(
            ConversionTask.status == 'FAILED'
        ).count()
        
        today_tasks = db.query(ConversionTask).filter(
            func.date(ConversionTask.created_at) == today
        ).count()
        
        total_orders = db.query(Order).count()
        paid_orders = db.query(Order).filter(Order.status == 'PAID').count()
        total_revenue = db.query(func.sum(Order.amount)).filter(
            Order.status == 'PAID'
        ).scalar() or 0.0
        
        today_revenue = db.query(func.sum(Order.amount)).filter(
            Order.status == 'PAID',
            func.date(Order.paid_at) == today
        ).scalar() or 0.0
        
        # 显示关键指标
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_users}</div>
                <div class="metric-label">👥 总用户数</div>
            </div>
            """, unsafe_allow_html=True)
            st.metric("今日新增", today_users)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <div class="metric-value">{total_tasks}</div>
                <div class="metric-label">📝 总转换任务</div>
            </div>
            """, unsafe_allow_html=True)
            st.metric("今日任务", today_tasks)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                <div class="metric-value">{format_currency(total_revenue)}</div>
                <div class="metric-label">💰 总收入</div>
            </div>
            """, unsafe_allow_html=True)
            st.metric("今日收入", format_currency(today_revenue))
        
        with col4:
            success_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
                <div class="metric-value">{success_rate:.1f}%</div>
                <div class="metric-label">✅ 成功率</div>
            </div>
            """, unsafe_allow_html=True)
            st.metric("活跃用户", active_users)
        
        st.markdown("---")
        
        # 转换任务状态分布
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.info(f"⏳ 待处理: {pending_tasks}")
        with col2:
            st.warning(f"🔄 进行中: {processing_tasks}")
        with col3:
            st.success(f"✅ 已完成: {completed_tasks}")
        with col4:
            st.error(f"❌ 失败: {failed_tasks}")
        
        # 最近活动
        st.markdown("### 🕒 最近活动")
        
        tab1, tab2, tab3 = st.tabs(["最近用户", "最近任务", "最近订单"])
        
        with tab1:
            recent_users = db.query(User).order_by(desc(User.created_at)).limit(10).all()
            if recent_users:
                user_data = []
                for user in recent_users:
                    user_data.append({
                        "用户ID": str(user.id)[:8] + "...",
                        "昵称": user.wechat_nickname or user.username or "-",
                        "剩余段落": user.paragraphs_remaining,
                        "余额": format_currency(user.balance),
                        "注册时间": format_datetime(user.created_at)
                    })
                st.dataframe(user_data, use_container_width=True, hide_index=True)
            else:
                st.info("暂无用户数据")
        
        with tab2:
            recent_tasks = db.query(ConversionTask).order_by(
                desc(ConversionTask.created_at)
            ).limit(10).all()
            if recent_tasks:
                task_data = []
                for task in recent_tasks:
                    status_emoji = {
                        'PENDING': '⏳',
                        'PROCESSING': '🔄',
                        'COMPLETED': '✅',
                        'FAILED': '❌'
                    }.get(task.status, '❓')
                    
                    task_data.append({
                        "任务ID": task.task_id[:12] + "...",
                        "文件名": task.filename or "-",
                        "段落数": task.paragraphs or "-",
                        "状态": f"{status_emoji} {task.status}",
                        "进度": f"{task.progress}%",
                        "创建时间": format_datetime(task.created_at)
                    })
                st.dataframe(task_data, use_container_width=True, hide_index=True)
            else:
                st.info("暂无任务数据")
        
        with tab3:
            recent_orders = db.query(Order).order_by(desc(Order.created_at)).limit(10).all()
            if recent_orders:
                order_data = []
                for order in recent_orders:
                    status_emoji = {
                        'PENDING': '⏳',
                        'PAID': '✅',
                        'FAILED': '❌',
                        'REFUNDED': '↩️'
                    }.get(order.status, '❓')
                    
                    order_data.append({
                        "订单号": order.order_no[:12] + "...",
                        "金额": format_currency(order.amount),
                        "段落数": order.paragraphs,
                        "套餐": order.package_label or "-",
                        "状态": f"{status_emoji} {order.status}",
                        "支付时间": format_datetime(order.paid_at)
                    })
                st.dataframe(order_data, use_container_width=True, hide_index=True)
            else:
                st.info("暂无订单数据")
    
    finally:
        db.close()

# ==================== 用户管理 ====================

def show_user_management():
    """显示用户管理"""
    st.title("👥 用户管理")
    st.markdown("---")
    
    db = get_db_session()
    
    try:
        # 搜索和筛选
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_keyword = st.text_input("🔍 搜索用户", placeholder="输入微信OpenID、昵称或用户名")
        
        with col2:
            sort_by = st.selectbox("排序方式", ["注册时间", "剩余段落", "余额"])
        
        with col3:
            show_count = st.selectbox("显示数量", [20, 50, 100], index=0)
        
        # 构建查询
        query = db.query(User)
        
        if search_keyword:
            query = query.filter(
                (User.wechat_openid.like(f"%{search_keyword}%")) |
                (User.wechat_nickname.like(f"%{search_keyword}%")) |
                (User.username.like(f"%{search_keyword}%"))
            )
        
        # 排序
        if sort_by == "注册时间":
            query = query.order_by(desc(User.created_at))
        elif sort_by == "剩余段落":
            query = query.order_by(desc(User.paragraphs_remaining))
        elif sort_by == "余额":
            query = query.order_by(desc(User.balance))
        
        # 分页
        total = query.count()
        users = query.limit(show_count).all()
        
        st.info(f"共找到 {total} 个用户，显示前 {len(users)} 个")
        
        if users:
            # 显示用户列表
            user_data = []
            for user in users:
                user_data.append({
                    "用户ID": str(user.id),
                    "微信OpenID": user.wechat_openid or "-",
                    "昵称": user.wechat_nickname or user.username or "-",
                    "剩余段落": user.paragraphs_remaining,
                    "余额": user.balance,
                    "状态": "✅ 活跃" if user.is_active else "❌ 禁用",
                    "注册时间": format_datetime(user.created_at)
                })
            
            st.dataframe(user_data, use_container_width=True, hide_index=True)
            
            # 用户操作
            st.markdown("### 🔧 用户操作")
            
            selected_user_id = st.text_input("输入用户ID进行操作", placeholder="粘贴完整的用户ID")
            
            if selected_user_id:
                user = db.query(User).filter(User.id == selected_user_id).first()
                
                if user:
                    st.success(f"找到用户: {user.wechat_nickname or user.username}")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        new_paragraphs = st.number_input(
                            "调整剩余段落",
                            value=int(user.paragraphs_remaining),
                            step=100,
                            key=f"para_{selected_user_id}"
                        )
                        if st.button("保存段落数", key=f"save_para_{selected_user_id}"):
                            user.paragraphs_remaining = new_paragraphs
                            db.commit()
                            st.success("✅ 段落数已更新")
                            st.rerun()
                    
                    with col2:
                        new_balance = st.number_input(
                            "调整余额",
                            value=float(user.balance),
                            step=1.0,
                            key=f"balance_{selected_user_id}"
                        )
                        if st.button("保存余额", key=f"save_balance_{selected_user_id}"):
                            user.balance = new_balance
                            db.commit()
                            st.success("✅ 余额已更新")
                            st.rerun()
                    
                    with col3:
                        new_status = st.selectbox(
                            "账户状态",
                            ["活跃", "禁用"],
                            index=0 if user.is_active else 1,
                            key=f"status_{selected_user_id}"
                        )
                        if st.button("更新状态", key=f"save_status_{selected_user_id}"):
                            user.is_active = (new_status == "活跃")
                            db.commit()
                            st.success("✅ 状态已更新")
                            st.rerun()
                else:
                    st.error("❌ 未找到该用户")
        else:
            st.warning("未找到匹配的用户")
    
    finally:
        db.close()

# ==================== 转换任务管理 ====================

def show_task_management():
    """显示转换任务管理"""
    st.title("📝 转换任务管理")
    st.markdown("---")
    
    db = get_db_session()
    
    try:
        # 筛选条件
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.selectbox(
                "任务状态",
                ["全部", "PENDING", "PROCESSING", "COMPLETED", "FAILED"]
            )
        
        with col2:
            date_filter = st.date_input("筛选日期", value=None)
        
        with col3:
            task_limit = st.selectbox("显示数量", [20, 50, 100], index=0)
        
        # 构建查询
        query = db.query(ConversionTask)
        
        if status_filter != "全部":
            query = query.filter(ConversionTask.status == status_filter)
        
        if date_filter:
            query = query.filter(
                func.date(ConversionTask.created_at) == date_filter
            )
        
        query = query.order_by(desc(ConversionTask.created_at))
        
        total = query.count()
        tasks = query.limit(task_limit).all()
        
        st.info(f"共找到 {total} 个任务，显示前 {len(tasks)} 个")
        
        if tasks:
            task_data = []
            for task in tasks:
                status_emoji = {
                    'PENDING': '⏳',
                    'PROCESSING': '🔄',
                    'COMPLETED': '✅',
                    'FAILED': '❌'
                }.get(task.status, '❓')
                
                task_data.append({
                    "任务ID": task.task_id,
                    "用户ID": str(task.user_id)[:8] + "...",
                    "文件名": task.filename or "-",
                    "段落数": task.paragraphs or "-",
                    "费用": f"¥{task.cost:.2f}" if task.cost else "-",
                    "状态": f"{status_emoji} {task.status}",
                    "进度": f"{task.progress}%",
                    "错误信息": task.error_message or "-",
                    "创建时间": format_datetime(task.created_at),
                    "完成时间": format_datetime(task.completed_at)
                })
            
            st.dataframe(task_data, use_container_width=True, hide_index=True)
            
            # 任务操作
            st.markdown("### 🔧 任务操作")
            
            selected_task_id = st.text_input("输入任务ID进行操作", placeholder="粘贴完整的任务ID")
            
            if selected_task_id:
                task = db.query(ConversionTask).filter(
                    ConversionTask.task_id == selected_task_id
                ).first()
                
                if task:
                    st.success(f"找到任务: {task.filename}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("标记为完成", key=f"complete_{selected_task_id}"):
                            task.status = 'COMPLETED'
                            task.progress = 100
                            task.completed_at = datetime.now()
                            db.commit()
                            st.success("✅ 任务已标记为完成")
                            st.rerun()
                    
                    with col2:
                        if st.button("标记为失败", key=f"fail_{selected_task_id}"):
                            task.status = 'FAILED'
                            db.commit()
                            st.success("✅ 任务已标记为失败")
                            st.rerun()
                    
                    if task.error_message:
                        st.error(f"错误信息: {task.error_message}")
                else:
                    st.error("❌ 未找到该任务")
        else:
            st.warning("未找到匹配的任务")
    
    finally:
        db.close()

# ==================== 订单管理 ====================

def show_order_management():
    """显示订单管理"""
    st.title("💰 订单管理")
    st.markdown("---")
    
    db = get_db_session()
    
    try:
        # 筛选条件
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.selectbox(
                "订单状态",
                ["全部", "PENDING", "PAID", "FAILED", "REFUNDED"]
            )
        
        with col2:
            date_filter = st.date_input("筛选日期", value=None)
        
        with col3:
            order_limit = st.selectbox("显示数量", [20, 50, 100], index=0)
        
        # 构建查询
        query = db.query(Order)
        
        if status_filter != "全部":
            query = query.filter(Order.status == status_filter)
        
        if date_filter:
            query = query.filter(func.date(Order.created_at) == date_filter)
        
        query = query.order_by(desc(Order.created_at))
        
        total = query.count()
        orders = query.limit(order_limit).all()
        
        st.info(f"共找到 {total} 个订单，显示前 {len(orders)} 个")
        
        if orders:
            order_data = []
            for order in orders:
                status_emoji = {
                    'PENDING': '⏳',
                    'PAID': '✅',
                    'FAILED': '❌',
                    'REFUNDED': '↩️'
                }.get(order.status, '❓')
                
                order_data.append({
                    "订单号": order.order_no,
                    "用户ID": str(order.user_id)[:8] + "...",
                    "金额": format_currency(order.amount),
                    "段落数": order.paragraphs,
                    "套餐": order.package_label or "-",
                    "支付方式": order.payment_method or "-",
                    "状态": f"{status_emoji} {order.status}",
                    "交易号": order.transaction_id or "-",
                    "创建时间": format_datetime(order.created_at),
                    "支付时间": format_datetime(order.paid_at)
                })
            
            st.dataframe(order_data, use_container_width=True, hide_index=True)
            
            # 订单操作
            st.markdown("### 🔧 订单操作")
            
            selected_order_no = st.text_input("输入订单号进行操作", placeholder="粘贴完整的订单号")
            
            if selected_order_no:
                order = db.query(Order).filter(
                    Order.order_no == selected_order_no
                ).first()
                
                if order:
                    st.success(f"找到订单: ¥{order.amount:.2f}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if order.status == 'PENDING':
                            if st.button("标记为已支付", key=f"pay_{selected_order_no}"):
                                order.status = 'PAID'
                                order.paid_at = datetime.now()
                                db.commit()
                                
                                # 给用户增加段落数
                                user = db.query(User).filter(User.id == order.user_id).first()
                                if user:
                                    user.paragraphs_remaining += order.paragraphs
                                    db.commit()
                                
                                st.success("✅ 订单已标记为已支付，用户段落数已增加")
                                st.rerun()
                    
                    with col2:
                        if order.status == 'PAID':
                            if st.button("标记为退款", key=f"refund_{selected_order_no}"):
                                order.status = 'REFUNDED'
                                db.commit()
                                
                                # 扣除用户段落数
                                user = db.query(User).filter(User.id == order.user_id).first()
                                if user:
                                    user.paragraphs_remaining -= order.paragraphs
                                    db.commit()
                                
                                st.success("✅ 订单已标记为退款，用户段落数已扣除")
                                st.rerun()
                else:
                    st.error("❌ 未找到该订单")
        else:
            st.warning("未找到匹配的订单")
    
    finally:
        db.close()

# ==================== 系统配置 ====================

def show_system_config():
    """显示系统配置"""
    st.title("⚙️ 系统配置")
    st.markdown("---")
    
    db = get_db_session()
    
    try:
        # 免费额度配置
        st.markdown("### 🎁 免费额度配置")
        
        config = db.query(SystemConfig).filter(
            SystemConfig.config_key == "free_paragraphs_on_first_login"
        ).first()
        
        if not config:
            config = SystemConfig(
                config_key="free_paragraphs_on_first_login",
                config_value="10000",
                description="新用户首次登录赠送的免费段落数"
            )
            db.add(config)
            db.commit()
            db.refresh(config)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            new_free_paragraphs = st.number_input(
                "首次登录赠送段落数",
                value=int(config.config_value),
                min_value=0,
                step=1000,
                help="新用户微信扫码登录后自动获得的免费段落数"
            )
        
        with col2:
            if st.button("💾 保存配置", use_container_width=True):
                if new_free_paragraphs < 0:
                    st.error("❌ 免费段落数不能为负数")
                else:
                    config.config_value = str(new_free_paragraphs)
                    db.commit()
                    st.success(f"✅ 配置已更新：新用户首次登录赠送 {new_free_paragraphs} 段")
                    st.rerun()
        
        st.info(f"📝 当前配置说明：{config.description}")
        st.caption(f"最后更新：{format_datetime(config.updated_at)}")
        
        st.markdown("---")
        
        # 其他配置项
        st.markdown("### 📋 所有配置项")
        
        all_configs = db.query(SystemConfig).order_by(SystemConfig.config_key).all()
        
        if all_configs:
            config_data = []
            for cfg in all_configs:
                config_data.append({
                    "配置键": cfg.config_key,
                    "配置值": cfg.config_value,
                    "说明": cfg.description or "-",
                    "更新时间": format_datetime(cfg.updated_at)
                })
            st.dataframe(config_data, use_container_width=True, hide_index=True)
        else:
            st.info("暂无其他配置项")
    
    finally:
        db.close()

# ==================== 主界面 ====================

def main():
    """主函数"""
    
    # 侧边栏导航
    with st.sidebar:
        st.header("🔧 WordStyle Pro 管理后台")
        st.markdown("---")
        
        page = st.radio(
            "选择页面",
            [
                "📊 数据看板",
                "👥 用户管理",
                "📝 转换任务",
                "💰 订单管理",
                "⚙️ 系统配置"
            ],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.caption("© 2026 WordStyle Pro")
        st.caption("版本: v2.9.0")
    
    # 根据选择显示不同页面
    if page == "📊 数据看板":
        show_dashboard()
    elif page == "👥 用户管理":
        show_user_management()
    elif page == "📝 转换任务":
        show_task_management()
    elif page == "💰 订单管理":
        show_order_management()
    elif page == "⚙️ 系统配置":
        show_system_config()

if __name__ == "__main__":
    main()

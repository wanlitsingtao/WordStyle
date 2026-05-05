# -*- coding: utf-8 -*-
"""
后台管理页面 - 数据统计、转换记录、配置管理
"""
import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="管理后台 - 文档转换工具",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 辅助函数 ====================

def load_all_user_data():
    """加载所有用户数据"""
    data_file = Path("user_data.json")
    if data_file.exists():
        with open(data_file, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def load_feedback_data():
    """加载反馈数据"""
    feedback_file = Path("feedback_data.json")
    if feedback_file.exists():
        with open(feedback_file, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def load_comment_data():
    """加载评论数据"""
    comment_file = Path("comments_data.json")
    if comment_file.exists():
        with open(comment_file, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def delete_comment(comment_id):
    """删除评论"""
    comment_file = Path("comments_data.json")
    if comment_file.exists():
        with open(comment_file, 'r', encoding='utf-8') as f:
            try:
                comments = json.load(f)
                comments = [c for c in comments if c['id'] != comment_id]
                # 重新编号
                for i, c in enumerate(comments):
                    c['id'] = i + 1
                with open(comment_file, 'w', encoding='utf-8') as fw:
                    json.dump(comments, fw, ensure_ascii=False, indent=2)
                return True
            except:
                return False
    return False

def load_conversion_stats():
    """加载转换统计信息"""
    # 从任务数据库读取（这里简化处理，实际应该查询数据库）
    return {
        'total_conversions': 0,
        'today_conversions': 0,
        'success_rate': 0
    }

# ==================== 主界面 ====================

def main():
    st.title("🔧 管理后台")
    st.markdown("---")
    
    # 侧边栏导航
    with st.sidebar:
        st.header("📊 导航")
        page = st.radio(
            "选择页面",
            ["📈 数据概览", "👥 用户管理", "💬 反馈管理", "💭 评论管理", "⚙️ 系统配置"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.caption("© 2026 文档转换工具")
    
    # 根据选择显示不同页面
    if page == "📈 数据概览":
        show_dashboard()
    elif page == "👥 用户管理":
        show_user_management()
    elif page == "💬 反馈管理":
        show_feedback_management()
    elif page == "💭 评论管理":
        show_comment_management()
    elif page == "⚙️ 系统配置":
        show_system_config()

def show_dashboard():
    """显示数据概览"""
    st.header("📈 数据概览")
    
    # 加载数据
    user_data = load_all_user_data()
    feedback_data = load_feedback_data()
    
    # 计算统计数据
    total_users = len(user_data)
    total_revenue = sum(u.get('balance', 0) for u in user_data.values())
    total_conversions = sum(u.get('total_converted', 0) for u in user_data.values())
    total_paragraphs_used = sum(u.get('total_paragraphs_used', 0) for u in user_data.values())
    total_feedback = len(feedback_data)
    
    # 显示关键指标
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("总用户数", f"{total_users:,}")
    with col2:
        st.metric("总收入", f"¥{total_revenue:.2f}")
    with col3:
        st.metric("总转换数", f"{total_conversions:,}")
    with col4:
        st.metric("总段落使用", f"{total_paragraphs_used:,}")
    with col5:
        st.metric("反馈数量", total_feedback)
    
    st.markdown("---")
    
    # 用户分布图表
    st.subheader("👥 用户活跃度分析")
    
    if user_data:
        # 按余额分组
        active_users = sum(1 for u in user_data.values() if u.get('paragraphs_remaining', 0) > 0)
        inactive_users = total_users - active_users
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("活跃用户", active_users)
        with col2:
            st.metric("非活跃用户", inactive_users)
        
        # 显示前10名用户
        st.subheader("🏆 Top 10 用户（按转换次数）")
        sorted_users = sorted(
            user_data.items(),
            key=lambda x: x[1].get('total_converted', 0),
            reverse=True
        )[:10]
        
        for idx, (user_id, data) in enumerate(sorted_users, 1):
            with st.expander(f"#{idx} 用户: {user_id[:8]}..."):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**转换次数:** {data.get('total_converted', 0)}")
                with col2:
                    st.write(f"**剩余段落:** {data.get('paragraphs_remaining', 0):,}")
                with col3:
                    st.write(f"**余额:** ¥{data.get('balance', 0):.2f}")
                
                # 显示充值历史
                if data.get('recharge_history'):
                    st.write("**充值记录:**")
                    for recharge in data['recharge_history'][-3:]:  # 最近3次
                        st.caption(f"- {recharge.get('time', '')}: +{recharge.get('paragraphs', 0):,}段")
    else:
        st.info("暂无用户数据")
    
    st.markdown("---")
    
    # 反馈统计
    st.subheader("💬 反馈统计")
    
    if feedback_data:
        # 按类型统计
        type_stats = {}
        status_stats = {}
        
        for fb in feedback_data:
            fb_type = fb.get('type', 'other')
            fb_status = fb.get('status', 'pending')
            
            type_stats[fb_type] = type_stats.get(fb_type, 0) + 1
            status_stats[fb_status] = status_stats.get(fb_status, 0) + 1
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**按类型分布:**")
            for fb_type, count in type_stats.items():
                type_names = {
                    'feature': '功能建议',
                    'bug': 'Bug报告',
                    'question': '使用问题',
                    'other': '其他'
                }
                st.write(f"- {type_names.get(fb_type, fb_type)}: {count}")
        
        with col2:
            st.write("**按状态分布:**")
            status_names = {
                'pending': '待处理',
                'reviewing': '审核中',
                'completed': '已完成',
                'rejected': '已拒绝'
            }
            for fb_status, count in status_stats.items():
                st.write(f"- {status_names.get(fb_status, fb_status)}: {count}")
    else:
        st.info("暂无反馈数据")

def show_user_management():
    """显示用户管理"""
    st.header("👥 用户管理")
    
    user_data = load_all_user_data()
    
    if not user_data:
        st.info("暂无用户数据")
        return
    
    # 搜索框
    search_query = st.text_input("🔍 搜索用户ID", placeholder="输入用户ID进行搜索")
    
    # 过滤用户
    filtered_users = user_data
    if search_query:
        filtered_users = {
            uid: data for uid, data in user_data.items()
            if search_query.lower() in uid.lower()
        }
    
    st.write(f"共找到 {len(filtered_users)} 个用户")
    
    # 显示用户列表
    for user_id, data in list(filtered_users.items())[:50]:  # 最多显示50个
        with st.expander(f"👤 {user_id[:12]}..."):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("余额", f"¥{data.get('balance', 0):.2f}")
            with col2:
                st.metric("剩余段落", f"{data.get('paragraphs_remaining', 0):,}")
            with col3:
                st.metric("转换次数", data.get('total_converted', 0))
            with col4:
                st.metric("使用段落", f"{data.get('total_paragraphs_used', 0):,}")
            
            # 操作按钮
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("查看充值记录", key=f"view_recharge_{user_id}"):
                    if data.get('recharge_history'):
                        st.write("**充值历史:**")
                        for recharge in data['recharge_history']:
                            st.caption(f"- {recharge.get('time', '')}: +{recharge.get('paragraphs', 0):,}段 (¥{recharge.get('amount', 0):.2f})")
                    else:
                        st.info("无充值记录")
            
            with col2:
                if st.button("查看转换记录", key=f"view_conversion_{user_id}"):
                    if data.get('conversion_history'):
                        st.write("**转换历史:**")
                        for conv in data['conversion_history'][-5:]:  # 最近5次
                            st.caption(f"- {conv.get('time', '')}: {conv.get('file_name', '未知文件')}")
                    else:
                        st.info("无转换记录")
            
            with col3:
                new_balance = st.number_input(
                    "调整余额",
                    value=data.get('balance', 0),
                    step=1.0,
                    key=f"balance_{user_id}"
                )
                if st.button("保存", key=f"save_{user_id}"):
                    # TODO: 实现余额调整功能
                    st.success("余额已更新（演示）")

def show_feedback_management():
    """显示反馈管理"""
    st.header("💬 反馈管理")
    
    feedback_data = load_feedback_data()
    
    if not feedback_data:
        st.info("暂无反馈数据")
        return
    
    # 筛选器
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox(
            "筛选状态",
            ["全部", "待处理", "审核中", "已完成", "已拒绝"]
        )
    with col2:
        type_filter = st.selectbox(
            "筛选类型",
            ["全部", "功能建议", "Bug报告", "使用问题", "其他"]
        )
    
    # 过滤反馈
    filtered_feedback = feedback_data
    
    if status_filter != "全部":
        status_map = {
            "待处理": "pending",
            "审核中": "reviewing",
            "已完成": "completed",
            "已拒绝": "rejected"
        }
        filtered_feedback = [
            fb for fb in filtered_feedback
            if fb.get('status') == status_map.get(status_filter)
        ]
    
    if type_filter != "全部":
        type_map = {
            "功能建议": "feature",
            "Bug报告": "bug",
            "使用问题": "question",
            "其他": "other"
        }
        filtered_feedback = [
            fb for fb in filtered_feedback
            if fb.get('type') == type_map.get(type_filter)
        ]
    
    st.write(f"共找到 {len(filtered_feedback)} 条反馈")
    
    # 显示反馈列表
    for fb in filtered_feedback:
        status_emoji = {
            'pending': '⏳',
            'reviewing': '🔍',
            'completed': '✅',
            'rejected': '❌'
        }
        
        type_emoji = {
            'feature': '💡',
            'bug': '🐛',
            'question': '❓',
            'other': '📝'
        }
        
        with st.expander(
            f"{status_emoji.get(fb.get('status'), '📄')} "
            f"{type_emoji.get(fb.get('type'), '📝')} "
            f"{fb.get('title', '无标题')} "
            f"(ID: {fb.get('feedback_id', '')[-8:]})"
        ):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**用户ID:** {fb.get('user_id', '')[:12]}...")
            with col2:
                st.write(f"**提交时间:** {fb.get('created_at', '')}")
            with col3:
                st.write(f"**状态:** {fb.get('status', 'pending')}")
            
            st.write(f"**类型:** {fb.get('type', 'other')}")
            st.write(f"**描述:**")
            st.write(fb.get('description', ''))
            
            if fb.get('contact'):
                st.write(f"**联系方式:** {fb.get('contact')}")
            
            if fb.get('admin_reply'):
                st.success(f"**管理员回复:** {fb.get('admin_reply')}")
            
            # 操作
            col1, col2, col3 = st.columns(3)
            with col1:
                new_status = st.selectbox(
                    "更新状态",
                    ["pending", "reviewing", "completed", "rejected"],
                    index=["pending", "reviewing", "completed", "rejected"].index(fb.get('status', 'pending')),
                    key=f"status_{fb.get('feedback_id')}"
                )
            with col2:
                admin_reply = st.text_input(
                    "管理员回复",
                    value=fb.get('admin_reply', ''),
                    key=f"reply_{fb.get('feedback_id')}"
                )
            with col3:
                if st.button("保存", key=f"save_fb_{fb.get('feedback_id')}"):
                    # TODO: 实现更新功能
                    st.success("状态已更新（演示）")

def show_comment_management():
    """显示评论管理"""
    st.header("💭 评论管理")
    
    # 加载评论数据
    comments = load_comment_data()
    
    # 统计信息
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总评论数", len(comments))
    with col2:
        if comments:
            avg_rating = sum(c.get('rating', 5) for c in comments) / len(comments)
            st.metric("平均评分", f"{avg_rating:.1f} ⭐")
        else:
            st.metric("平均评分", "暂无")
    with col3:
        total_likes = sum(c.get('likes', 0) for c in comments)
        st.metric("总点赞数", total_likes)
    
    st.markdown("---")
    
    if not comments:
        st.info("💭 暂无评论")
        return
    
    # 筛选器
    col1, col2 = st.columns(2)
    with col1:
        rating_filter = st.selectbox(
            "筛选评分",
            ["全部", "5星", "4星", "3星", "2星", "1星"]
        )
    with col2:
        sort_by = st.selectbox(
            "排序方式",
            ["时间倒序", "时间正序", "点赞数降序", "评分降序"]
        )
    
    # 应用筛选
    filtered_comments = comments.copy()
    if rating_filter != "全部":
        rating_map = {"5星": 5, "4星": 4, "3星": 3, "2星": 2, "1星": 1}
        target_rating = rating_map.get(rating_filter, 5)
        filtered_comments = [c for c in filtered_comments if c.get('rating') == target_rating]
    
    # 应用排序
    if sort_by == "时间倒序":
        filtered_comments.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    elif sort_by == "时间正序":
        filtered_comments.sort(key=lambda x: x.get('timestamp', ''))
    elif sort_by == "点赞数降序":
        filtered_comments.sort(key=lambda x: x.get('likes', 0), reverse=True)
    elif sort_by == "评分降序":
        filtered_comments.sort(key=lambda x: x.get('rating', 5), reverse=True)
    
    st.markdown(f"**显示 {len(filtered_comments)} 条评论**")
    st.markdown("---")
    
    # 分页设置
    if len(filtered_comments) > 0:
        col_page1, col_page2, col_page3 = st.columns([2, 2, 2])
        with col_page1:
            page_size = st.selectbox(
                "每页显示",
                [10, 20, 50, 100],
                index=1,  # 默认20条
                key="comment_page_size"
            )
        
        # 计算总页数
        total_pages = (len(filtered_comments) + page_size - 1) // page_size
        
        with col_page2:
            current_page = st.number_input(
                "当前页",
                min_value=1,
                max_value=total_pages,
                value=1,
                step=1,
                key="comment_current_page"
            )
        
        with col_page3:
            st.write(f"**共 {total_pages} 页**")
        
        # 计算当前页的数据范围
        start_idx = (current_page - 1) * page_size
        end_idx = min(start_idx + page_size, len(filtered_comments))
        paginated_comments = filtered_comments[start_idx:end_idx]
        
        st.caption(f"显示第 {start_idx + 1}-{end_idx} 条，共 {len(filtered_comments)} 条")
    else:
        paginated_comments = []
    
    st.markdown("---")
    
    # 准备表格数据
    table_data = []
    for comment in paginated_comments:
        stars = "⭐" * comment.get('rating', 5)
        table_data.append({
            'ID': comment['id'],
            '评分': stars,
            '评论内容': comment.get('content', '')[:50] + ('...' if len(comment.get('content', '')) > 50 else ''),
            '点赞数': comment.get('likes', 0),
            '用户ID': comment.get('user_id', '未知')[:12],
            '时间': comment.get('timestamp', '')
        })
    
    # 显示表格
    if table_data:
        import pandas as pd
        df = pd.DataFrame(table_data)
        st.dataframe(
            df,
            use_container_width=True,
            height=400,
            hide_index=True,
            column_config={
                "ID": st.column_config.NumberColumn("ID", width="small"),
                "评分": st.column_config.TextColumn("评分", width="medium"),
                "评论内容": st.column_config.TextColumn("评论内容", width="large"),
                "点赞数": st.column_config.NumberColumn("点赞数", width="small"),
                "用户ID": st.column_config.TextColumn("用户ID", width="medium"),
                "时间": st.column_config.TextColumn("时间", width="medium")
            }
        )
    else:
        st.info("💭 暂无评论数据")
    
    st.markdown("---")
    
    # 批量操作区域
    st.subheader("🔧 批量操作")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        # 选择要删除的评论ID（仅当前页）
        comment_ids = [c['id'] for c in paginated_comments]
        if comment_ids:
            selected_ids = st.multiselect(
                "选择要删除的评论ID（当前页）",
                comment_ids,
                help="可以选择多个评论进行批量删除"
            )
        else:
            st.write("当前页无评论")
            selected_ids = []
    
    with col2:
        st.write("")  # 占位
        st.write("")  # 占位
        if st.button("🗑️ 删除选中评论", type="primary", disabled=not selected_ids):
            success_count = 0
            for cid in selected_ids:
                if delete_comment(cid):
                    success_count += 1
            if success_count > 0:
                st.success(f"✅ 成功删除 {success_count} 条评论")
                st.rerun()
            else:
                st.error("❌ 删除失败")
    
    with col3:
        st.write("")  # 占位
        st.write("")  # 占位
        if st.button("⚠️ 清空所有评论", type="secondary"):
            st.warning("此操作不可恢复！请在确认对话框中再次确认。")
            if st.button("✅ 确认清空所有评论", type="primary"):
                comment_file = Path("comments_data.json")
                if comment_file.exists():
                    with open(comment_file, 'w', encoding='utf-8') as f:
                        json.dump([], f)
                    st.success("✅ 已清空所有评论")
                    st.rerun()

def show_system_config():
    """显示系统配置"""
    st.header("⚙️ 系统配置")
    
    # 免费额度配置
    st.subheader("🎁 免费额度设置")
    
    # 读取当前配置
    config_file = Path("system_config.json")
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            try:
                config = json.load(f)
            except:
                config = {'free_paragraphs_on_first_login': 10000}
    else:
        config = {'free_paragraphs_on_first_login': 10000}
    
    free_paragraphs = st.number_input(
        "新用户首次登录赠送段落数",
        value=config.get('free_paragraphs_on_first_login', 10000),
        min_value=0,
        step=1000,
        help="新用户首次访问时自动获得的免费段落数"
    )
    
    if st.button("💾 保存配置", type="primary"):
        config['free_paragraphs_on_first_login'] = free_paragraphs
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        st.success("✅ 配置已保存！")
    
    st.markdown("---")
    
    # 充值档位配置
    st.subheader("💳 充值档位设置")
    st.info("充值档位请在 app.py 中的 RECHARGE_PACKAGES 变量中修改")
    
    st.markdown("---")
    
    # 系统信息
    st.subheader("ℹ️ 系统信息")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**版本:** v2.0")
        st.write(f"**最后更新:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    with col2:
        st.write(f"**Python版本:** {sys.version.split()[0]}")
        st.write(f"**Streamlit版本:** {st.__version__}")

if __name__ == "__main__":
    main()

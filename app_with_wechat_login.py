# -*- coding: utf-8 -*-
"""
文档转换工具 - Web 版本（带微信登录）
基于 Streamlit + FastAPI 后端
"""
import streamlit as st
import os
import sys
import json
import threading
import requests
import time
from datetime import datetime, timedelta
from pathlib import Path

# 添加当前目录到路径，以便导入 doc_converter
sys.path.insert(0, os.path.dirname(__file__))

from doc_converter import DocumentConverter
from task_manager import (
    create_task, update_task_status, complete_task, fail_task,
    get_user_active_task, get_user_completed_tasks, has_active_task,
    cleanup_expired_tasks, RESULTS_DIR
)

# ==================== 配置 ====================
BACKEND_URL = "http://localhost:8000"  # 后端API地址
PARAGRAPH_PRICE = 0.001  # 每个段落的价格（元）

# 充值档位
RECHARGE_PACKAGES = [
    {'amount': 1, 'paragraphs': 1000, 'label': '体验版'},
    {'amount': 5, 'paragraphs': 5000, 'label': '标准版'},
    {'amount': 10, 'paragraphs': 10000, 'label': '专业版'},
    {'amount': 50, 'paragraphs': 50000, 'label': '企业版'},
    {'amount': 100, 'paragraphs': 100000, 'label': '旗舰版'},
]

ADMIN_CONTACT = "微信号：your_wechat_id"  # 管理员联系方式

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="标书抄写神器",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 初始化会话状态 ====================
if 'user_id' not in st.session_state:
    # 生成匿名用户ID
    import hashlib
    import time
    unique_key = f"{time.time()}_{id(st.session_state)}"
    st.session_state.user_id = hashlib.md5(unique_key.encode()).hexdigest()[:12]
    st.session_state.is_anonymous = True  # 标记为匿名用户

if 'free_paragraphs_claimed' not in st.session_state:
    st.session_state.free_paragraphs_claimed = False  # 是否已领取免费额度

# ==================== 自定义CSS ====================
st.markdown("""
<style>
    /* 隐藏页脚 */
    footer {visibility: hidden;}
    
    /* 强制主要内容区域使用最大宽度 */
    .block-container {
        max-width: 100% !important;
        padding-top: 2rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* 优化文件上传器大小 */
    .stFileUploader > div {
        min-height: 80px;
    }
    
    /* 增大按钮 */
    .stButton > button {
        height: 3em;
        font-size: 1.1em;
        width: 100%;
    }
    
    /* 优化指标显示 */
    [data-testid="stMetric"] {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 5px;
    }
    
    /* 修复侧边栏隐藏后的布局问题 */
    div[data-testid="stAppViewContainer"] {
        width: 100% !important;
    }
    
    section[data-testid="stSidebar"] + div {
        flex-grow: 1 !important;
        width: auto !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 辅助函数 ====================

def get_free_paragraphs_config():
    """获取免费额度配置"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/admin/config/free-paragraphs", timeout=3)
        if response.status_code == 200:
            data = response.json()
            return data.get('config_value', 10000)
        return 10000
    except:
        return 10000

def load_user_data():
    """加载用户数据（本地JSON文件）"""
    user_id = st.session_state.user_id
    data_file = Path("user_data.json")
    
    if data_file.exists():
        with open(data_file, 'r', encoding='utf-8') as f:
            try:
                all_data = json.load(f)
                return all_data.get(user_id, {
                    'balance': 0.0,
                    'paragraphs_remaining': 0,
                    'total_converted': 0,
                    'total_paragraphs_used': 0,
                    'recharge_history': [],
                    'conversion_history': []
                })
            except:
                pass
    
    return {
        'balance': 0.0,
        'paragraphs_remaining': 0,
        'total_converted': 0,
        'total_paragraphs_used': 0,
        'recharge_history': [],
        'conversion_history': []
    }

def save_user_data(user_data):
    """保存用户数据"""
    user_id = st.session_state.user_id
    data_file = Path("user_data.json")
    
    all_data = {}
    if data_file.exists():
        with open(data_file, 'r', encoding='utf-8') as f:
            try:
                all_data = json.load(f)
            except:
                pass
    
    all_data[user_id] = user_data
    
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

def claim_free_paragraphs():
    """领取免费额度（仅首次）"""
    if st.session_state.free_paragraphs_claimed:
        return 0
    
    free_paragraphs = get_free_paragraphs_config()
    user_data = load_user_data()
    user_data['paragraphs_remaining'] += free_paragraphs
    save_user_data(user_data)
    
    st.session_state.free_paragraphs_claimed = True
    return free_paragraphs

# ==================== 主应用逻辑 ====================

def show_recharge_qr():
    """显示充值二维码"""
    st.markdown("---")
    st.subheader("💳 扫码充值")
    
    # 充值档位选择
    package_options = [f"{pkg['label']} - ¥{pkg['amount']} ({pkg['paragraphs']:,}段)" for pkg in RECHARGE_PACKAGES]
    selected_package = st.selectbox("选择充值档位", package_options)
    
    if st.button("生成支付二维码", type="primary", use_container_width=True):
        # 提取金额
        for pkg in RECHARGE_PACKAGES:
            if f"{pkg['label']} - ¥{pkg['amount']}" in selected_package:
                amount = pkg['amount']
                paragraphs = pkg['paragraphs']
                break
        
        # TODO: 调用后端API创建订单并获取真实二维码
        # 当前显示模拟二维码
        st.success(f"✅ 请扫描下方二维码转账 ¥{amount}")
        st.info("💡 扫码后会自动识别您的用户ID并充值")
        
        # 显示占位二维码
        st.image(
            "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICAgIDxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjZjdmYWZjIi8+CiAgICA8dGV4dCB4PSI1MCUiIHk9IjUwJSIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjE0IiBmaWxsPSIjYTBhZWMwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+CiAgICAgICAg5byA5aeL5LiJ5q+B5L2gCiAgICA8L3RleHQ+Cjwvc3ZnPg==",
            caption=f"模拟支付二维码（生产环境应显示真实微信收款码）\n\n用户ID: {st.session_state.user_id}",
            width=200
        )
        
        st.warning("⚠️ **演示模式**\n\n当前为模拟支付，实际使用时需要：\n1. 接入微信支付API\n2. 生成真实的收款二维码\n3. 监听支付回调自动充值")

def main():
    """主应用"""
    
    # 首次访问，自动领取免费额度
    if not st.session_state.free_paragraphs_claimed:
        free_paragraphs = claim_free_paragraphs()
        if free_paragraphs > 0:
            st.toast(f"🎉 欢迎！已赠送您 {free_paragraphs:,} 段免费额度", icon="🎁")
    
    # 加载用户数据
    user_data = load_user_data()
    
    # ==================== 侧边栏 ====================
    with st.sidebar:
        st.header("👤 用户信息")
        
        # 显示用户ID
        st.markdown(f"""
        <div style='background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>
            <small>用户ID</small><br>
            <code style='font-size: 0.9em;'>{st.session_state.user_id}</code>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 显示余额和段落数
        col1, col2 = st.columns(2)
        with col1:
            st.metric("剩余段落", f"{user_data.get('paragraphs_remaining', 0):,}")
        with col2:
            st.metric("账户余额", f"¥{user_data.get('balance', 0):.2f}")
        
        st.markdown("---")
        
        # 充值二维码区域
        show_recharge_qr()
        
        st.markdown("---")
        
        # 管理员联系方式
        st.caption(f"📞 如需帮助，请联系：{ADMIN_CONTACT}")
    
    # ==================== 主内容区域 ====================
    st.title("📝 标书抄写神器")
    
    st.markdown("""
    <div style='background-color: #e3f2fd; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>
    💡 <strong>提示：</strong>按 <kbd>F11</kbd> 键可以让浏览器全屏显示，获得更好的体验
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 这里可以继续添加原有的转换功能...
    st.info("🚧 文档转换功能正在集成中...")
    
    # TODO: 将原有的转换功能代码迁移到这里
    # 需要修改的地方：
    # 1. 使用后端API进行用户认证
    # 2. 调用后端API开始转换任务
    # 3. 从后端获取转换结果

if __name__ == "__main__":
    main()

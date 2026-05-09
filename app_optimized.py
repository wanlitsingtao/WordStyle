# -*- coding: utf-8 -*-
"""
文档转换工具 - Web 版本 (高性能优化版)
基于 Streamlit 快速搭建
优化重点：减少不必要的重渲染，提升交互响应速度
"""
import streamlit as st
import os
import sys
import json
import threading
import logging
from datetime import datetime, timedelta
from pathlib import Path
from contextlib import contextmanager

# 配置日志系统
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('WordStyle')

# 添加当前目录到路径，以便导入其他模块
sys.path.insert(0, os.path.dirname(__file__))

# 导入配置
from config import (
    PARAGRAPH_PRICE, MIN_RECHARGE, BACKEND_URL, RECHARGE_PACKAGES,
    ADMIN_CONTACT, FREE_PARAGRAPHS_DAILY, RESULTS_DIR,
    DEFAULT_ANSWER_TEXT, DEFAULT_ANSWER_STYLE, DEFAULT_ANSWER_MODE,
    ANSWER_MODE_OPTIONS, DEFAULT_LIST_BULLET, PAGE_TITLE, PAGE_ICON,
    LAYOUT, SIDEBAR_STATE
)

# 导入工具函数
from utils import (
    sanitize_html, sanitize_filename, validate_docx_file,
    calculate_cost, format_number
)

# 导入用户管理
from user_manager import (
    load_user_data, save_user_data, claim_free_paragraphs,
    recharge_user, deduct_paragraphs, add_conversion_record,
    get_user_stats, generate_user_id
)

# 导入评论管理
from comments_manager import (
    load_comments, save_comments, add_comment, like_comment,
    get_comments, get_comment_stats, validate_comment_content,
    add_feedback, get_feedbacks, get_feedback_stats
)

# 导入临时文件清理模块
from temp_file_cleanup import cleanup_on_startup

# 导入转换器
from doc_converter import DocumentConverter
from task_manager import (
    create_task, update_task_status, complete_task, fail_task,
    get_user_active_task, get_user_completed_tasks, has_active_task,
    cleanup_expired_tasks
)

# ==================== 性能优化：使用fragment隔离高频更新区域 ====================

# 缓存稳定的options引用，避免每次重渲染都重建
@st.cache_data(ttl=3600)
def get_answer_mode_options():
    """获取应答句插入模式选项（带缓存，保持引用稳定）"""
    return {
        'before_heading': '章节前插入',
        'after_heading': '章节后插入',
        'copy_chapter': '章节招标原文+应答句+招标原文副本',
        'before_paragraph': '逐段前应答',
        'after_paragraph': '逐段后应答'
    }

@st.fragment
def render_conversion_config():
    """
    渲染转换配置区（使用fragment优化性能）
    
    优化点：
    1. 使用@st.fragment隔离，避免用户交互导致全局重渲染
    2. 仅在值真正改变时才更新session_state
    3. 预计算索引，避免重复遍历
    """
    
    # 第一行：四个选项横向等距分布
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 样式映射", key="open_style_mapping_btn", use_container_width=True, 
                    help="如果不采用系统给的默认配置，可自定义样式映射"):
            st.session_state.show_style_mapping_dialog = True
    
    with col2:
        do_mood = st.checkbox(
            "祈使语气转换", 
            value=st.session_state.do_mood_config, 
            help="将文档中的祈使语气转换为投标人语气",
            key="mood_checkbox"
        )
        # 仅在值改变时更新session_state，避免不必要的重渲染
        if do_mood != st.session_state.do_mood_config:
            st.session_state.do_mood_config = do_mood
    
    with col3:
        do_answer = st.checkbox(
            "插入应答句", 
            value=st.session_state.do_answer_config, 
            help="在标题后插入应答句",
            key="answer_checkbox"
        )
        # 仅在值改变时更新session_state
        if do_answer != st.session_state.do_answer_config:
            st.session_state.do_answer_config = do_answer
    
    with col4:
        list_bullet = st.text_input(
            "列表符号", 
            value=st.session_state.list_bullet_config, 
            help="列表段落的符号",
            key="bullet_input"
        )
        # 仅在值改变时更新session_state
        if list_bullet != st.session_state.list_bullet_config:
            st.session_state.list_bullet_config = list_bullet
    
    # 第二行：应答句详细配置（仅当勾选"插入应答句"时显示）
    if do_answer:
        st.markdown("---")
        st.markdown("** 应答句配置**")
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            answer_text = st.text_input(
                "应答句文本",
                value=st.session_state.answer_text_config,
                help="插入的应答句内容",
                key="answer_text_input"
            )
            # 仅在值改变时更新
            if answer_text != st.session_state.answer_text_config:
                st.session_state.answer_text_config = answer_text
        
        with col_b:
            # 获取模板样式列表（使用缓存的引用）
            template_styles = st.session_state.get('template_styles', ["Normal"])
            
            # 预计算index，避免每次渲染都查找
            style_index = 0
            if st.session_state.answer_style_config in template_styles:
                try:
                    style_index = template_styles.index(st.session_state.answer_style_config)
                except ValueError:
                    style_index = 0
            
            answer_style = st.selectbox(
                "应答句样式",
                options=template_styles,
                index=style_index,
                help="应答句的段落样式",
                key="answer_style_select"
            )
            # 仅在值改变时更新
            if answer_style != st.session_state.answer_style_config:
                st.session_state.answer_style_config = answer_style
        
        with col_c:
            # 使用缓存的options，保持引用稳定
            answer_mode_options = get_answer_mode_options()
            
            # 预计算mode_keys和index，避免每次渲染都创建新列表
            if 'answer_mode_keys_cache' not in st.session_state:
                st.session_state.answer_mode_keys_cache = list(answer_mode_options.keys())
            mode_keys = st.session_state.answer_mode_keys_cache
            
            # 预计算index
            mode_index = 0
            if st.session_state.answer_mode_config in answer_mode_options:
                try:
                    mode_index = mode_keys.index(st.session_state.answer_mode_config)
                except ValueError:
                    mode_index = 0
            
            answer_mode = st.selectbox(
                "插入模式",
                options=mode_keys,
                format_func=lambda x: answer_mode_options[x],
                index=mode_index,
                help="应答句的插入位置模式",
                key="answer_mode_select"
            )
            # 仅在值改变时更新
            if answer_mode != st.session_state.answer_mode_config:
                st.session_state.answer_mode_config = answer_mode
    else:
        # 不插入应答句时使用默认值
        answer_text = st.session_state.answer_text_config
        answer_style = st.session_state.answer_style_config
        answer_mode = st.session_state.answer_mode_config
    
    # 返回配置值供后续使用
    return do_mood, do_answer, list_bullet, answer_text, answer_style, answer_mode


# ==================== 示例：如何使用优化后的配置区 ====================

if __name__ == "__main__":
    # 初始化session_state（实际使用时这部分代码应该放在app.py的初始化部分）
    if 'do_mood_config' not in st.session_state:
        st.session_state.do_mood_config = True
    if 'do_answer_config' not in st.session_state:
        st.session_state.do_answer_config = True
    if 'list_bullet_config' not in st.session_state:
        st.session_state.list_bullet_config = "•"
    if 'answer_text_config' not in st.session_state:
        st.session_state.answer_text_config = "应答：本投标人理解并满足要求。"
    if 'answer_style_config' not in st.session_state:
        st.session_state.answer_style_config = "Normal"
    if 'answer_mode_config' not in st.session_state:
        st.session_state.answer_mode_config = 'before_heading'
    if 'template_styles' not in st.session_state:
        st.session_state.template_styles = ["Normal", "Heading 1", "Heading 2"]
    
    st.title(" WordStyle Pro - 高性能优化版")
    st.markdown("---")
    
    # 使用优化后的配置区
    config_result = render_conversion_config()
    do_mood, do_answer, list_bullet, answer_text, answer_style, answer_mode = config_result
    
    # 显示当前配置（仅用于演示）
    st.markdown("---")
    st.markdown("**📊 当前配置状态**")
    st.json({
        "祈使语气转换": do_mood,
        "插入应答句": do_answer,
        "列表符号": list_bullet,
        "应答句文本": answer_text,
        "应答句样式": answer_style,
        "插入模式": answer_mode
    })

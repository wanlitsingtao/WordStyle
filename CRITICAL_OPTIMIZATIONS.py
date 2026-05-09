# -*- coding: utf-8 -*-
"""
关键性能优化 - 直接替换app.py中的关键部分
"""

# ==================== 优化1: 样式映射对话框（使用fragment） ====================

@st.fragment(run_every=1)  # 使用fragment隔离，避免全局重渲染
def show_style_mapping_dialog():
    """显示样式映射配置对话框（优化性能版）"""
    st.markdown("**请为源文档中的每个样式选择对应的模板样式：**")
    st.markdown("_（未配置的样式将使用系统默认映射规则）_")
    
    # 从 session_state 获取已分析的样式
    file_styles_map = st.session_state.get('file_styles_map', {})
    template_styles = st.session_state.get('template_styles', [])
    source_files = st.session_state.get('current_source_files', None)
    
    if not file_styles_map or not source_files:
        st.warning("️ 请先上传源文档并等待样式分析完成")
        return
    
    if not template_styles:
        st.warning("⚠️ 请先上传模板文档")
        return
    
    # 初始化或加载样式映射（按文件分别存储）
    if 'file_style_mappings' not in st.session_state:
        from user_manager import load_style_mappings
        st.session_state.file_style_mappings = load_style_mappings()
    
    # 如果有多个文件，先选择要配置的文件
    selected_file = None
    if len(source_files) > 1:
        file_options = [sf.name for sf in source_files]
        selected_file_name = st.selectbox("选择要配置的文件", file_options, key="style_mapping_file_selector")
        selected_file = next(sf for sf in source_files if sf.name == selected_file_name)
    else:
        selected_file = source_files[0]
    
    # 获取该文件的样式列表
    source_styles = file_styles_map.get(selected_file.name, [])
    
    if not source_styles:
        st.warning(f"️ 文件 {selected_file.name} 中没有检测到段落样式")
        return
    
    # 获取该文件的当前映射配置
    if selected_file.name not in st.session_state.file_style_mappings:
        st.session_state.file_style_mappings[selected_file.name] = {}
    
    current_mapping = st.session_state.file_style_mappings[selected_file.name]
    
    # 预计算所有默认值和index，避免在循环中重复计算
    default_values = {}
    style_indices = {}
    for source_style in source_styles:
        if source_style in current_mapping:
            default_values[source_style] = current_mapping[source_style]
        elif source_style in template_styles:
            default_values[source_style] = source_style
        else:
            default_values[source_style] = "Normal"
        
        # 预计算index
        style_index = 0
        if default_values[source_style] in template_styles:
            try:
                style_index = template_styles.index(default_values[source_style])
            except ValueError:
                style_index = 0
        style_indices[source_style] = style_index
    
    # 缓存template_styles的引用，避免每次渲染都传递
    template_styles_cached = template_styles
    
    # 为每个源样式创建映射行（参照桌面版逻辑）
    updated_mapping = {}
    for source_style in source_styles:
        col1, col2, col3 = st.columns([2.5, 2.5, 1])
        
        with col1:
            st.text(source_style)
        
        with col2:
            # 使用预计算的值
            selected = st.selectbox(
                "→",
                options=template_styles_cached,
                index=style_indices[source_style],
                key=f"mapping_{selected_file.name}_{source_style}",
                label_visibility="collapsed"
            )
            updated_mapping[source_style] = selected
        
        with col3:
            hint = "✓ 已配置" if source_style in current_mapping else "○ 使用默认"
            color = "green" if source_style in current_mapping else "gray"
            st.markdown(f"<span style='color:{color};font-size:0.9em;'>{hint}</span>", unsafe_allow_html=True)
    
    # 保存更新后的映射
    st.session_state.file_style_mappings[selected_file.name] = updated_mapping
    
    # 操作按钮
    st.markdown("---")
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    
    with btn_col1:
        if st.button("✅ 确定", key="confirm_mapping_btn", type="primary", use_container_width=True):
            from user_manager import save_style_mappings
            save_style_mappings(st.session_state.file_style_mappings)
            st.success("✅ 样式映射已保存！")
            st.rerun()
    
    with btn_col2:
        if st.button("🔄 恢复默认", key="reset_mapping_btn", use_container_width=True):
            st.session_state.file_style_mappings[selected_file.name] = {}
            from user_manager import save_style_mappings
            save_style_mappings(st.session_state.file_style_mappings)
            st.rerun()
    
    with btn_col3:
        if st.button("❌ 取消", key="cancel_mapping_btn", use_container_width=True):
            st.session_state.show_style_mapping_dialog = False


# ==================== 优化2: 转换配置区（使用fragment） ====================

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

@st.fragment(run_every=1)  # 使用fragment隔离配置区
def render_conversion_config():
    """渲染转换配置区（优化性能版）"""
    
    # 第一行：四个选项横向等距分布
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button(" 样式映射", key="open_style_mapping_btn", use_container_width=True, help="如果不采用系统给的默认配置，可自定义样式映射"):
            st.session_state.show_style_mapping_dialog = True
    
    with col2:
        do_mood = st.checkbox(
            "祈使语气转换", 
            value=st.session_state.do_mood_config, 
            help="将文档中的祈使语气转换为投标人语气",
            key="mood_checkbox"
        )
        if do_mood != st.session_state.do_mood_config:
            st.session_state.do_mood_config = do_mood
    
    with col3:
        do_answer = st.checkbox(
            "插入应答句", 
            value=st.session_state.do_answer_config, 
            help="在标题后插入应答句",
            key="answer_checkbox"
        )
        if do_answer != st.session_state.do_answer_config:
            st.session_state.do_answer_config = do_answer
    
    with col4:
        list_bullet = st.text_input(
            "列表符号", 
            value=st.session_state.list_bullet_config, 
            help="列表段落的符号",
            key="bullet_input"
        )
        if list_bullet != st.session_state.list_bullet_config:
            st.session_state.list_bullet_config = list_bullet
    
    # 第二行：应答句详细配置
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
            if answer_text != st.session_state.answer_text_config:
                st.session_state.answer_text_config = answer_text
        
        with col_b:
            template_styles = st.session_state.get('template_styles', ["Normal"])
            
            # 预计算index
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
            if answer_style != st.session_state.answer_style_config:
                st.session_state.answer_style_config = answer_style
        
        with col_c:
            answer_mode_options = get_answer_mode_options()
            
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
            if answer_mode != st.session_state.answer_mode_config:
                st.session_state.answer_mode_config = answer_mode
    else:
        answer_text = st.session_state.answer_text_config
        answer_style = st.session_state.answer_style_config
        answer_mode = st.session_state.answer_mode_config
    
    return do_mood, do_answer, list_bullet, answer_text, answer_style, answer_mode


# ==================== 优化3: 开始转换按钮（快速响应） ====================

def render_start_conversion_button(source_files, template_file, do_mood, do_answer, list_bullet, answer_text, answer_style, answer_mode):
    """渲染开始转换按钮（优化响应速度）"""
    st.markdown("---")
    
    # 检查是否有进行中的任务
    active_task = has_active_task(st.session_state.user_id)
    
    if active_task:
        st.warning(f"⚠️ **您有一个进行中的后台任务**\n\n文件名：{active_task['filename']}\n状态：{active_task['status']}")
        if active_task['status'] == 'PROCESSING':
            st.progress(active_task['progress'] / 100.0)
            st.text(f"转换进度：{active_task['progress']}%")
        st.info("💡 您可以在下方的「转换历史」中查看任务状态和下载完成的文件")
    else:
        is_converting = st.session_state.get('is_converting', False)
        
        if is_converting:
            st.warning("⏳ **正在进行前台转换，请稍候...**")
            st.info("💡 转换完成后将自动恢复操作权限")
        else:
            button_disabled = has_active_task(st.session_state.user_id)
            
            if st.button("🚀 开始转换", type="primary", use_container_width=True, disabled=button_disabled):
                if not source_files or not template_file:
                    st.error("❌ 请上传源文档和模板文档")
                elif 'temp_template' not in locals():
                    st.error("❌ 文件上传失败，请重试")
                else:
                    if has_active_task(st.session_state.user_id):
                        active_task = get_user_active_task(st.session_state.user_id)
                        st.error(f"❌ 您已有进行中的任务：{active_task['filename']}")
                        st.stop()
                    
                    st.session_state.is_converting = True
                    
                    # 立即显示进度条
                    progress_placeholder = st.empty()
                    status_placeholder = st.empty()
                    progress_bar = progress_placeholder.progress(0)
                    status_placeholder.text("⏳ 正在准备转换...")
                    progress_bar.progress(5)
                    
                    # 统计总段落数
                    total_paragraphs = sum(count_paragraphs(f"temp_source_{st.session_state.user_id}_{sf.name}") for sf in source_files)
                    cost = calculate_cost(total_paragraphs)
                    
                    user_data = st.session_state.user_data
                    
                    if total_paragraphs > user_data['paragraphs_remaining']:
                        st.error(f" 余额不足！需要 {total_paragraphs:,} 个段落（¥{cost:.2f}），剩余 {user_data['paragraphs_remaining']:,} 个")
                        st.info("💡 请在左侧充值中心充值")
                        st.stop()
                    
                    # 准备文件信息
                    source_files_info = []
                    for sf in source_files:
                        temp_source = f"temp_source_{st.session_state.user_id}_{sf.name}"
                        file_paragraphs = count_paragraphs(temp_source)
                        source_files_info.append((sf.name, temp_source, file_paragraphs))
                    
                    # 配置字典
                    config = {
                        'do_mood': do_mood,
                        'answer_text': answer_text,
                        'answer_style': answer_style,
                        'list_bullet': list_bullet if list_bullet else "•",
                        'do_answer_insertion': do_answer,
                        'answer_mode': answer_mode,
                        'custom_style_map': st.session_state.get('style_mapping', None)
                    }
                    
                    # 继续转换逻辑...
                    return True, source_files_info, config, progress_placeholder, status_placeholder, progress_bar
    
    return False, None, None, None, None, None

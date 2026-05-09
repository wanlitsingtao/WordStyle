# -*- coding: utf-8 -*-
"""
Streamlit 页面灰化优化脚本
自动移除不必要的 st.rerun() 调用
"""
import re
from pathlib import Path

def optimize_rerun_calls(file_path):
    """优化app.py中的st.rerun()调用"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_lines = content.count('\n')
    
    # 1. 第989行 - 上传收款码后（不必要）
    # 查找并移除
    pattern1 = r'(with open\(qr_code_path, \'wb\'\) as f:\s+f\.write\(uploaded_file\.read\(\)\)\s+st\.success\("✅ 收款码已保存！"\))\s+st\.rerun\(\)'
    replacement1 = r'\1\n                    # ✅ 已移除st.rerun()，页面会自动检测到文件存在'
    content = re.sub(pattern1, replacement1, content)
    
    # 2. 第1033行 - 取消订单（用session_state代替）
    pattern2 = r'(if st\.button\("❌ 取消", use_container_width=True, key=f"cancel_\{order_id\}"\):\s+st\.info\("订单已取消"\)\s+time\.sleep\(1\))\s+st\.rerun\(\)'
    replacement2 = r'''\1
                            # ✅ 使用session_state标记，避免st.rerun()
                            st.session_state.show_recharge_dialog = False
                            st.session_state.current_order_id = None'''
    content = re.sub(pattern2, replacement2, content)
    
    # 3. 第1123行 - 取消反馈表单（用session_state代替）
    pattern3 = r'(if cancel_feedback:\s+st\.session_state\.show_feedback_form = False)\s+st\.rerun\(\)'
    replacement3 = r'''\1
        # ✅ 已移除st.rerun()，session_state变化会触发自然重渲染'''
    content = re.sub(pattern3, replacement3, content)
    
    # 4. 第1979行 - 取消样式映射（直接移除）
    pattern4 = r'(if st\.button\("❌ 取消", key="cancel_mapping_btn", use_container_width=True\):\s+)st\.rerun\(\)'
    replacement4 = r'''\1# ✅ 已移除st.rerun()
            st.session_state.show_style_mapping_dialog = False'''
    content = re.sub(pattern4, replacement4, content)
    
    # 保存修改后的文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    new_lines = content.count('\n')
    
    print(f"✅ 优化完成！")
    print(f"   原始行数: {original_lines}")
    print(f"   优化后行数: {new_lines}")
    print(f"   变化: {new_lines - original_lines:+d} 行")
    
    return True

if __name__ == "__main__":
    app_file = Path(__file__).parent / "app.py"
    
    if not app_file.exists():
        print(f"❌ 文件不存在: {app_file}")
        exit(1)
    
    print("🔧 开始优化 st.rerun() 调用...")
    print("=" * 60)
    
    optimize_rerun_calls(app_file)
    
    print("\n💡 提示: 请手动检查以下位置的优化:")
    print("   - 评论区点赞功能（第508行附近）")
    print("   - 充值相关功能（第1021、1027、1049行）- 这些需要保留")
    print("   - 样式映射确认/重置（第1967、1975行）- 可选优化")

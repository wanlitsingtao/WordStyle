# -*- coding: utf-8 -*-
"""多页面包 views/

[NOTE] 2026-09-10 由 pages/ 改名为 views/，从源头消除 Streamlit 默认多页导航
的首帧 FOUC 闪现。Streamlit 仅把名为 pages/ 的目录识别为自动多页面入口；
views/ 是普通 Python 包，不再触发前端默认导航生成，配合 app.py 的
st.navigation(position="hidden") 与 CSS 兜底，实现「首帧即正确、无闪现」。
"""

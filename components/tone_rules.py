# -*- coding: utf-8 -*-
"""
祈使语气规则编辑组件（T02）
渲染投标称谓 / 祈使词 / 标志动词 / 例外词，支持浏览 / 增 / 删 / 改。

编辑区顺序（2026-11-18 用户定）：
  1. 投标人称谓替换   2. 祈使词替换（多字 + 单字合为一张表）
  3. 应+对分离结构标志动词   4. 例外词列表

采用 st.data_editor（映射表）+ st.text_area（列表）实现：
- 替换映射（原词 → 替换词）用可动态增删行的表格编辑。
- 祈使词表把多字 / 单字规则合成一张「原词/替换词」两列表；用户不必选类型，
  返回规则时按**原词字数**自动归位（1 字 → single_imperative，2 字及以上 →
  multi_imperative），转换逻辑不变。
- 例外词 / 标志动词用"每行一个词"的文本域编辑。

组件为纯渲染函数，返回用户当前编辑后的规则字典（工作副本），
持久化由 views/tone_config.py 负责。
"""
import logging

import streamlit as st


logger = logging.getLogger('WordStyle')


def _render_mapping_editor(rules, category, editor_key, label):
    """渲染一个"原词 → 替换词"映射的 data_editor。

    返回更新后的 rules 字典（原地更新 category 键）。
    """
    import pandas as pd

    mapping = rules.get(category, {}) or {}

    if mapping:
        df = pd.DataFrame(
            [{"原词": k, "替换词": v} for k, v in mapping.items()],
            columns=["原词", "替换词"],
        )
    else:
        df = pd.DataFrame(columns=["原词", "替换词"])

    edited = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        key=editor_key,
        column_config={
            "原词": st.column_config.TextColumn("原词", help="要被替换的词"),
            "替换词": st.column_config.TextColumn("替换词", help="替换后的词"),
        },
    )

    # 过滤空行并转换为字典（去除首尾空白；空原词/空替换词的行忽略）
    new_mapping = {}
    for _, row in edited.iterrows():
        src = str(row.get("原词", "") or "").strip()
        tgt = str(row.get("替换词", "") or "").strip()
        if src and tgt:
            new_mapping[src] = tgt
    rules[category] = new_mapping
    st.caption(f"当前 {label} 共 {len(new_mapping)} 条有效规则（空行将被忽略）")
    return rules


def _render_list_editor(rules, sub_key, editor_key, label, hint):
    """渲染一个"每行一个词"的文本域编辑器，用于例外词 / 标志动词列表。

    返回更新后的 rules 字典。
    """
    import re

    lst = rules.get(sub_key, []) or []
    initial_text = "\n".join(lst)

    edited_text = st.text_area(
        label,
        value=initial_text,
        key=editor_key,
        height=120,
        help=hint,
    )

    items = [w.strip() for w in re.split(r"[\n,，、]+", edited_text) if w.strip()]
    rules[sub_key] = items
    st.caption(f"当前共 {len(items)} 个词")
    return rules


def _render_imperative_editor(rules, editor_key):
    """多字 / 单字祈使词合并成一张「原词 → 替换词」两列表编辑。

    「类型（多字/单字）」对用户无意义，且完全可由原词字数确定，故界面不再提供该列：
    用户只需填原词与替换词，返回规则时按**原词字数**自动归位——
    1 字 → `single_imperative`，2 字及以上 → `multi_imperative`。

    两个规则集在转换引擎里使用不同的正则与例外词机制，因此数据结构仍保留拆分，
    tone_rules_manager / doc_converter 零改动。空原词 / 空替换词的行忽略，值做 strip()。
    """
    import pandas as pd

    multi = rules.get("multi_imperative", {}) or {}
    single = rules.get("single_imperative", {}) or {}

    rows = [{"原词": k, "替换词": v} for k, v in multi.items()]
    rows += [{"原词": k, "替换词": v} for k, v in single.items()]

    columns = ["原词", "替换词"]
    df = pd.DataFrame(rows, columns=columns) if rows else pd.DataFrame(columns=columns)

    edited = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        key=editor_key,
        column_config={
            "原词": st.column_config.TextColumn("原词", help="要被替换的词"),
            "替换词": st.column_config.TextColumn("替换词", help="替换后的词"),
        },
    )

    new_multi = {}
    new_single = {}
    for _, row in edited.iterrows():
        src = str(row.get("原词", "") or "").strip()
        tgt = str(row.get("替换词", "") or "").strip()
        if not src or not tgt:
            continue
        # 单字 / 多字由原词字数决定，不再需要用户填写类型
        if len(src) == 1:
            new_single[src] = tgt
        else:
            new_multi[src] = tgt

    rules["multi_imperative"] = new_multi
    rules["single_imperative"] = new_single
    st.caption(f"当前共 {len(new_multi) + len(new_single)} 条有效规则（空行将被忽略）")
    return rules


@st.fragment
def render_tone_rules_editor(rules):
    """渲染语气规则编辑区（@st.fragment 局部刷新）。

    Args:
        rules: 当前工作副本规则字典（会被原地更新并返回）。

    Returns:
        dict: 更新后的规则字典。
    """
    if not isinstance(rules, dict):
        rules = {}

    # 1. 投标人称谓替换
    bidder_count = len(rules.get("bidder_terms", {}) or {})
    with st.expander(
        f"▸ 投标人称谓替换（{bidder_count} 条）",
        expanded=False,
        key="tone_expand_bidder",
    ):
        rules = _render_mapping_editor(rules, "bidder_terms", "tone_editor_bidder", "投标人称谓替换")

    # 2. 祈使词替换（多字 + 单字合为一张两列表，按原词字数自动归类）
    imperative_count = (
        len(rules.get("multi_imperative", {}) or {})
        + len(rules.get("single_imperative", {}) or {})
    )
    with st.expander(
        f"▸ 祈使词替换（{imperative_count} 条）",
        expanded=False,
        key="tone_expand_imperative",
    ):
        rules = _render_imperative_editor(rules, "tone_editor_imperative")

    # 3. "应+对"分离结构标志动词
    verbs_count = len(rules.get("ying_dui_verbs", []) or [])
    with st.expander(
        f"▸ 应+对分离结构标志动词（{verbs_count} 个）",
        expanded=False,
        key="tone_expand_verbs",
    ):
        _render_list_editor(rules, "ying_dui_verbs", "tone_editor_verbs",
                            "标志动词（每行一个词）",
                            "用于检测「应+对+动词」分离结构（如「应对…负责」），避免误替换")

    # 4. 例外词列表（3 组）
    exceptions = rules.setdefault("exceptions", {})
    if not isinstance(exceptions, dict):
        exceptions = {}
        rules["exceptions"] = exceptions
    exc_total = (
        len(exceptions.get("multi", []) or [])
        + len(exceptions.get("ying", []) or [])
        + len(exceptions.get("xu", []) or [])
    )
    with st.expander(
        f"▸ 例外词列表（{exc_total} 个）",
        expanded=False,
        key="tone_expand_exceptions",
    ):
        col_a, col_b = st.columns(2)
        with col_a:
            _render_list_editor(exceptions, "multi", "tone_editor_exc_multi",
                                "多字祈使词例外（每行一个词）",
                                "这些词中即使包含祈使词也不会被替换")
        with col_b:
            _render_list_editor(exceptions, "ying", "tone_editor_exc_ying",
                                "「应」字例外词（每行一个词）",
                                "这些词中的「应」字不会被替换")

        _render_list_editor(exceptions, "xu", "tone_editor_exc_xu",
                            "「须」字例外词（每行一个词）",
                            "这些词中的「须」字不会被替换")

    return rules


# 编辑区涉及的 widget key 集合（供"恢复默认"后清理 session_state）
TONE_EDITOR_KEYS = (
    "tone_editor_bidder",
    "tone_editor_imperative",
    "tone_editor_verbs",
    "tone_editor_exc_multi",
    "tone_editor_exc_ying",
    "tone_editor_exc_xu",
)


def clear_tone_editor_state():
    """清理语气编辑器在 session_state 中缓存的 widget 状态。"""
    for key in TONE_EDITOR_KEYS:
        if key in st.session_state:
            del st.session_state[key]

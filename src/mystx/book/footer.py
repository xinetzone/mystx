"""内容页脚：把 ``book_footer_items`` 变成可直接渲染的数据。

与页眉按钮一样，页脚是"数据不是模板"：哪些条目、取哪个上下文变量、缺数据时是否
跳过，全在这里决定，模板只按 ``type`` 输出。
"""

from __future__ import annotations

from typing import Any

#: 支持的页脚条目
FOOTER_ITEMS = ("author", "copyright", "last-updated")


def build_footer(context: dict[str, Any], names: list[str]) -> list[dict[str, str]]:
    """按配置顺序生成页脚条目；缺数据或未知名称的条目直接跳过。"""
    items: list[dict[str, str]] = []
    for name in names:
        key = name.strip()
        if key == "author" and context.get("author"):
            items.append({"type": "author", "text": str(context["author"])})
        elif key == "copyright" and context.get("copyright"):
            items.append({"type": "copyright", "text": str(context["copyright"])})
        elif key == "last-updated" and context.get("last_updated"):
            items.append({"type": "last-updated", "text": str(context["last_updated"])})
    return items

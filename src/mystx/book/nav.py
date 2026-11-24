"""侧栏导航参数。

只决定"从哪里开始渲染"与"展开多深"，不重写 PST 的 toctree 算法。
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True, slots=True)
class SidebarKwargs:
    """``generate_toctree_html`` 的关键字参数（仅书籍层关心的子集）。"""

    startdepth: int
    show_nav_level: int
    maxdepth: int
    collapse: bool = False
    includehidden: bool = True
    titles_only: bool = True

    def to_kwargs(self) -> dict[str, Any]:
        """转成可直接展开的字典，模板用 ``**kw`` 传给 ``generate_toctree_html``。"""
        return asdict(self)


def sidebar_kwargs(
    scope: str,
    depth: int,
    maxdepth: int,
    collapse: Any = False,
) -> SidebarKwargs:
    """按阅读模型计算侧栏参数。

    Args:
        scope: ``"book"`` 渲染全书树；``"section"`` 渲染当前顶层章节子树。
        depth: 初始展开层数。
        maxdepth: 最大渲染层数。
        collapse: ``collapse_navigation`` 的配置值，布尔或字符串。

    Raises:
        ValueError: ``scope`` 不是已知取值。
    """
    if scope not in {"book", "section"}:
        raise ValueError(f"book_nav_scope must be 'book' or 'section', got {scope!r}")
    return SidebarKwargs(
        startdepth=0 if scope == "book" else 1,
        show_nav_level=max(1, int(depth)),
        maxdepth=max(1, int(maxdepth)),
        collapse=_as_bool(collapse),
    )

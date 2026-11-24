"""主题选项归一化。

``theme.conf`` 只能存字符串；在 ``builder-inited`` 阶段把书籍层选项转成模板
期望的类型，并注册侧栏参数函数供模板调用。
"""

from __future__ import annotations

from typing import Any

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.util import logging

from .buttons import build_buttons
from .footer import build_footer
from .nav import sidebar_kwargs

logger = logging.getLogger(__name__)


def _sidebar_kwargs_dict(*args: Any) -> dict[str, Any]:
    """模板用的包装：把 dataclass 展开成可 ``**kw`` 的字典。"""
    return sidebar_kwargs(*args).to_kwargs()

_LIST_OPTIONS = ("book_header_buttons", "book_footer_items")
_INT_OPTIONS = ("book_nav_depth", "navigation_depth")
_BOOL_OPTIONS = ("book_use_sidenotes",)
#: 会让正文内容落到右侧留白的节点类名（含 myst-nb 单元格标签）
_MARGIN_CLASSES = frozenset({"sidenote", "marginnote", "margin", "tag_margin", "tag_full-width", "tag_full_width"})


def _as_list(value: Any) -> list[str]:
    if isinstance(value, (list, tuple)):
        return [str(item).strip() for item in value if str(item).strip()]
    return [item.strip() for item in str(value).split(",") if item.strip()]


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _theme_options(app: Sphinx) -> dict[str, Any] | None:
    builder = getattr(app, "builder", None)
    options = getattr(builder, "theme_options", None)
    return options if isinstance(options, dict) else None


def get_theme_option(app: Sphinx, key: str, default: Any = None) -> Any:
    """读取单个主题选项（已由 :func:`normalize_theme_options` 归一化）。"""
    options = _theme_options(app) or {}
    return options.get(key, default)


def config_flag(config: Any, key: str, default: bool = False) -> bool:
    """从配置里读布尔选项：供只拿得到 ``config`` 的变换使用。"""
    options = getattr(config, "html_theme_options", None) or {}
    return _as_bool(options.get(key, default))


def normalize_theme_options(app: Sphinx) -> None:
    """把字符串选项转换为模板可直接使用的类型。"""
    options = _theme_options(app)
    if options is None:
        return

    for key in _LIST_OPTIONS:
        if key in options:
            options[key] = _as_list(options[key])
    for key in _INT_OPTIONS:
        if key in options:
            try:
                options[key] = int(options[key])
            except (TypeError, ValueError):
                logger.warning("mystx: invalid integer for %s: %r", key, options[key])
    for key in _BOOL_OPTIONS:
        if key in options:
            options[key] = _as_bool(options[key])

    scope = str(options.get("book_nav_scope", "book"))
    if scope not in {"book", "section"}:
        logger.warning("mystx: invalid book_nav_scope %r, falling back to 'book'", scope)
        options["book_nav_scope"] = "book"

    environment = getattr(getattr(app.builder, "templates", None), "environment", None)
    if environment is not None:
        environment.globals["book_sidebar_kwargs"] = _sidebar_kwargs_dict


def resolve_nav_scope(app: Sphinx, pagename: str, scope: str) -> str:
    """把 ``section`` 降级为 ``book``：无祖先页面（首页/搜索/索引）无法按章节渲染。"""
    if scope != "section":
        return "book"
    try:
        from pydata_sphinx_theme.toctree import _get_ancestor_pagename

        ancestor, _ = _get_ancestor_pagename(app, pagename, 1)
    except Exception:  # pragma: no cover - 上游私有 API 变化时的兜底
        return "book"
    return "section" if ancestor else "book"


def update_page_context(app: Sphinx, pagename: str, templatename: str, context: dict, doctree) -> None:
    """按页面决定侧栏范围、页眉按钮与留白布局，写入模板上下文。"""
    options = _theme_options(app) or {}
    scope = str(options.get("book_nav_scope", context.get("theme_book_nav_scope", "book")))
    context["mystx_nav_scope"] = resolve_nav_scope(app, pagename, scope)
    context["mystx_has_margin"] = page_has_margin(doctree)

    names = options.get("book_header_buttons") or context.get("theme_book_header_buttons") or []
    if isinstance(names, str):
        names = [item.strip() for item in names.split(",") if item.strip()]
    context["book_buttons"] = build_buttons(pagename, context, list(names))

    footer_names = options.get("book_footer_items")
    if footer_names is None:
        footer_names = context.get("theme_book_footer_items") or []
    if isinstance(footer_names, str):
        footer_names = [item.strip() for item in footer_names.split(",") if item.strip()]
    context["book_footer"] = build_footer(_footer_source(app, context), list(footer_names))


def _footer_source(app: Sphinx, context: dict) -> dict[str, Any]:
    """页脚数据源：模板上下文优先，缺失时回退 conf.py 的同名字段。"""
    source = dict(context)
    config = app.config
    for key in ("author", "copyright"):
        if not source.get(key):
            source[key] = getattr(config, key, None)
    return source


def page_has_margin(doctree) -> bool:
    """页面是否含边注/margin 内容：决定宽屏是否让出右侧目录栏。"""
    if doctree is None:
        return False
    findall = getattr(doctree, "findall", None)
    nodes_iter = findall(nodes.Element) if findall is not None else doctree.traverse(nodes.Element)
    for node in nodes_iter:
        classes = set(node.get("classes") or ())
        if classes & _MARGIN_CLASSES:
            return True
    return False

"""mystx - 面向书籍阅读的 Sphinx 主题。

基座为 ``pydata-sphinx-theme``；书籍能力（全书导航、页眉工具箱、边注）
作为本包自有模块实现。
"""

from __future__ import annotations

from pathlib import Path

from sphinx.application import Sphinx
from sphinx.util.typing import ExtensionMetadata

from .book.options import normalize_theme_options, update_nav_scope

try:  # setuptools-scm 在构建时写入；源码树内可能缺失
    from ._version import __version__
except ImportError:  # pragma: no cover
    try:
        from importlib.metadata import version as _pkg_version

        __version__ = _pkg_version("mystx")
    except Exception:  # pragma: no cover
        __version__ = "0.0.0.dev0"

__all__ = ["__version__", "setup"]


def setup(app: Sphinx) -> ExtensionMetadata:
    """注册主题与书籍能力。"""
    theme_dir = Path(__file__).parent / "theme" / "mystx"
    app.add_html_theme("mystx", str(theme_dir))
    app.add_css_file("css/book.css")
    app.connect("builder-inited", normalize_theme_options, priority=400)
    app.connect("html-page-context", update_nav_scope)
    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }

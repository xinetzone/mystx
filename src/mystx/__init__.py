"""mystx - 现代化 Sphinx 文档主题

This module provides a custom Sphinx theme for creating beautiful, modern documentation.
The theme includes configuration management, styling, and integration with Sphinx.
"""
from sphinx.application import Sphinx
from sphinx.util.typing import ExtensionMetadata
from myst_nb.sphinx_ext import sphinx_setup as setup_myst_nb
from .theme import MySTX
from .config import config_inited_handler


def setup(app: Sphinx) -> ExtensionMetadata:
    """Sphinx extension setup."""
    setup_myst_nb(app) # Markdown和Jupyter笔记本支持
    MySTX(app) # 自定义主题设置
    # 连接到配置初始化事件
    app.connect('config-inited', config_inited_handler)
    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }

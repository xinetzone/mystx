"""mystx - 现代化 Sphinx 文档主题。

This module provides a custom Sphinx theme for creating beautiful, modern documentation.
The theme includes configuration management, styling, and integration with Sphinx.
"""
from sphinx.application import Sphinx
from sphinx.util import logging
from sphinx.util.typing import ExtensionMetadata

from .theme import MySTX
from .config import config_inited_handler

logger = logging.getLogger(__name__)


def _setup_myst_nb(app: Sphinx) -> None:
    """注册 myst-nb 的 Markdown 与 Jupyter Notebook 支持。

    ``myst-nb`` 为可选依赖：缺失时仅记录日志并跳过，保证纯主题安装下
    ``import mystx`` 与主题注册不因缺失 ``myst-nb`` 而崩溃。
    """
    try:
        from myst_nb.sphinx_ext import sphinx_setup as setup_myst_nb
    except ImportError:
        logger.info("未安装 myst-nb，跳过 Markdown 与 Jupyter Notebook 支持")
        return
    setup_myst_nb(app)


def setup(app: Sphinx) -> ExtensionMetadata:
    """Sphinx extension setup."""
    _setup_myst_nb(app)  # Markdown 和 Jupyter 笔记本支持（可选依赖）
    MySTX(app)  # 自定义主题设置
    # 连接到配置初始化事件
    app.connect("config-inited", config_inited_handler)
    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
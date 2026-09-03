"""mystx - 现代化 Sphinx 文档主题。

This module provides a custom Sphinx theme for creating beautiful, modern documentation.
The theme includes configuration management, styling, and integration with Sphinx.
"""
try:
    from ._version import __version__
except ImportError:  # pragma: no cover - setuptools-scm 生成文件缺失时回退
    try:
        from importlib.metadata import version as _pkg_version
        __version__ = _pkg_version("mystx")
    except Exception:  # pragma: no cover - 开发环境无安装元数据时的最终回退
        __version__ = "0.0.0.dev0"

from sphinx.application import Sphinx
from sphinx.util import logging
from sphinx.util.typing import ExtensionMetadata

from .utils import deep_merge, has_module
from .themes import MySTX
from .config import config_inited_handler
from .configs import (DEFAULT_MYST_CONFIG, DEFAULT_BUILD_CONFIG, DEFAULT_EXT_CONFIG, DEFAULT_HTML_CONFIG, build_base_config)
from .extensions import (DEFAULT_OPTIONAL_EXTENSIONS, DEFAULT_CONDITIONAL, resolve_extensions)
from .themes import (DEFAULT_BOOK_THEME_OPTIONS, DEFAULT_THEME_PRIORITY, resolve_theme, resolve_theme_options)
from .myst_compat import register_hooks as register_myst_compat_hooks
from . import presets
from .presets import build_minimal_myst_config
from . import tasks

__all__ = ["__version__", "deep_merge", "has_module", "MySTX", "config_inited_handler", "setup", "logger", "DEFAULT_MYST_CONFIG", "DEFAULT_BUILD_CONFIG", "DEFAULT_EXT_CONFIG", "DEFAULT_HTML_CONFIG", "build_base_config", "DEFAULT_OPTIONAL_EXTENSIONS", "DEFAULT_CONDITIONAL", "resolve_extensions", "DEFAULT_BOOK_THEME_OPTIONS", "DEFAULT_THEME_PRIORITY", "resolve_theme", "resolve_theme_options", "register_myst_compat_hooks", "presets", "build_minimal_myst_config", "tasks"]

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
    # 注册 myst 兼容性钩子（source-read / doctree-read）
    register_myst_compat_hooks(app)
    # 自动注入 myst_parser
    extensions_list: list[str] = []
    if hasattr(app, "config") and hasattr(app.config, "extensions"):
        extensions_list = list(app.config.extensions)
    elif hasattr(app, "extensions"):
        extensions_list = list(getattr(app, "extensions", {}).keys())
    if "myst_parser" not in extensions_list:
        app.setup_extension("myst_parser")
        logger.warning("myst_parser not found in extensions list; mystx auto-injecting it. Install it explicitly to avoid this warning.")
    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
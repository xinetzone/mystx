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

from . import presets, tasks
from .config import config_inited_handler
from .configs import (
    DEFAULT_BUILD_CONFIG,
    DEFAULT_EXT_CONFIG,
    DEFAULT_HTML_CONFIG,
    DEFAULT_MYST_CONFIG,
    build_base_config,
)
from .extensions import DEFAULT_CONDITIONAL, DEFAULT_OPTIONAL_EXTENSIONS, resolve_extensions
from .myst_compat import register_hooks as register_myst_compat_hooks
from .presets import build_minimal_myst_config
from .themes import DEFAULT_BOOK_THEME_OPTIONS, DEFAULT_THEME_PRIORITY, MySTX, resolve_theme, resolve_theme_options
from .utils import deep_merge, has_module

__all__ = ["__version__", "deep_merge", "has_module", "MySTX", "config_inited_handler", "setup", "logger", "DEFAULT_MYST_CONFIG", "DEFAULT_BUILD_CONFIG", "DEFAULT_EXT_CONFIG", "DEFAULT_HTML_CONFIG", "build_base_config", "DEFAULT_OPTIONAL_EXTENSIONS", "DEFAULT_CONDITIONAL", "resolve_extensions", "DEFAULT_BOOK_THEME_OPTIONS", "DEFAULT_THEME_PRIORITY", "resolve_theme", "resolve_theme_options", "register_myst_compat_hooks", "presets", "build_minimal_myst_config", "tasks"]

logger = logging.getLogger(__name__)


def _setup_myst_nb(app: Sphinx) -> None:
    """注册 myst-nb 的 Jupyter Notebook 支持（可选依赖）。

    走 Sphinx 标准幂等入口 ``app.setup_extension``；缺失 myst-nb 时仅记录
    日志并跳过，保证纯主题安装下 ``import mystx`` 与主题注册不因此崩溃。
    """
    if not has_module("myst_nb"):
        logger.info("未安装 myst-nb，跳过 Jupyter Notebook 支持")
        return
    app.setup_extension("myst_nb")


def setup(app: Sphinx) -> ExtensionMetadata:
    """Sphinx extension setup."""
    configured = set(app.config.extensions) if hasattr(app, "config") else set()
    loaded = set(getattr(app, "extensions", {}).keys())

    # Markdown/Notebook 链加载契约（myst-parser 5.x / myst-nb 1.x）：
    # 两个扩展入口都调用同一个非幂等的 setup_sphinx()（内部对
    # registry.transforms 执行 list.remove），且都注册 .md 后缀，
    # 同时加载必然抛 ValueError/ExtensionError。myst_nb 内部已完成
    # myst_parser 的全部配置与 transforms 注册，其 parser 又是超集，
    # 因此采用互斥策略：nb 在场仅加载 nb，否则加载 parser；
    # 用户已在 conf 显式声明或提前加载任一者时尊重其选择，不再注入。
    markdown_chain = {"myst_parser", "myst_nb"}
    if not (configured & markdown_chain) and not (loaded & markdown_chain):
        if has_module("myst_nb"):
            _setup_myst_nb(app)
        else:
            app.setup_extension("myst_parser")
            logger.warning("myst_parser not found in extensions list; mystx auto-injecting it. Install it explicitly to avoid this warning.")

    MySTX(app)  # 自定义主题设置
    # 连接到配置初始化事件
    app.connect("config-inited", config_inited_handler)
    # 注册 myst 兼容性钩子（source-read / doctree-read）
    register_myst_compat_hooks(app)
    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }

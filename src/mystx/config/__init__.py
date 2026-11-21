"""mystx 配置层对外门面。

按**生效时点**二分内部模块，公共名统一从本包导出：

* :mod:`~mystx.config.defaults`：构建期静态默认与纯函数组装，产出
  conf.py 风格的核心配置字典；
* :mod:`~mystx.config.runtime`：运行期对 Sphinx ``Config`` 的注入与合并，
  由 ``config-inited`` 事件驱动。
"""

from .defaults import (
    BOOK_THEME_NAMES,
    BOOK_THEME_OPTION_DEFAULTS,
    DEFAULT_BUILD_CONFIG,
    DEFAULT_EXT_CONFIG,
    DEFAULT_HTML_CONFIG,
    DEFAULT_MYST_CONFIG,
    build_base_config,
)
from .runtime import (
    ConfigManager,
    apply_book_theme_option_defaults,
    config_inited_handler,
    thebe_setup,
)

__all__ = [
    "BOOK_THEME_NAMES",
    "BOOK_THEME_OPTION_DEFAULTS",
    "DEFAULT_BUILD_CONFIG",
    "DEFAULT_EXT_CONFIG",
    "DEFAULT_HTML_CONFIG",
    "DEFAULT_MYST_CONFIG",
    "ConfigManager",
    "apply_book_theme_option_defaults",
    "build_base_config",
    "config_inited_handler",
    "thebe_setup",
]
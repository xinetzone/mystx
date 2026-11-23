"""运行期配置：对已初始化的 Sphinx ``Config`` 做注入与合并，由 ``config-inited`` 驱动。

静态默认与纯函数组装（conf.py 风格字典）见 :mod:`mystx.config.defaults`。
"""
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.errors import ExtensionError
from sphinx.util import logging

from ..themes import BOOK_THEME_NAMES
from ..utils import deep_merge
from ..version_switcher import sphinx_setup as version_switcher_setup
from .defaults import BOOK_THEME_OPTION_DEFAULTS

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ConfigManager:
    """加载 ``<srcdir>/_config.toml`` 并合并到 ``html_theme_options``。"""

    app: Sphinx
    config: Config
    logger: logging.SphinxLoggerAdapter | None = None

    def __post_init__(self) -> None:
        self.logger = logging.getLogger(f"{__name__}.ConfigManager")

    def load_custom_config(self) -> dict[str, Any] | None:
        """读取 ``_config.toml``；文件不存在时返回 ``None``。"""
        custom_toml = Path(self.app.srcdir) / "_config.toml"
        if not custom_toml.exists():
            return None
        try:
            with custom_toml.open("rb") as f:
                return tomllib.load(f)
        except tomllib.TOMLDecodeError as exc:
            self.logger.error("自定义配置文件格式错误: %s", exc, exc_info=True)
            raise
        except OSError as exc:
            self.logger.error("加载自定义配置文件失败: %s", exc, exc_info=True)
            raise

    def apply_config(self) -> None:
        """把自定义配置应用到 ``Config``（当前仅 ``html_theme_options``）。"""
        custom_config = self.load_custom_config()
        if custom_config:
            self._merge_html_theme_options(custom_config)

    def _merge_html_theme_options(self, custom_config: dict[str, Any]) -> None:
        """``deep_merge`` 自定义主题选项，用户配置覆盖包内预设。"""
        overrides = custom_config.get("html_theme_options")
        if not overrides:
            return
        current = getattr(self.config, "html_theme_options", None) or {}
        self.config.html_theme_options = deep_merge(
            current, overrides, remove_marker=None
        )
        self.logger.info("已更新 html_theme_options")


def apply_book_theme_option_defaults(config: Config) -> None:
    """为书系主题补齐结构性 ``html_theme_options`` 默认项。

    ``setdefault`` 语义：键缺失时才注入，绝不覆盖用户在 conf.py 或
    ``_config.toml`` 中的显式声明；非书系主题直接返回。
    """
    if config.html_theme not in BOOK_THEME_NAMES:
        return
    options = getattr(config, "html_theme_options", None) or {}
    for key, value in BOOK_THEME_OPTION_DEFAULTS.items():
        options.setdefault(key, value)
    config.html_theme_options = options


def thebe_setup(app: Sphinx, config: Config) -> None:
    """装配 ``sphinx_thebe`` 并开启 Thebe 按钮；装配失败则整体放弃。"""
    if "sphinx_thebe" not in config.extensions:
        try:
            app.setup_extension("sphinx_thebe")
        except ExtensionError as exc:
            logger.warning("设置 sphinx_thebe 扩展时出错: %s", exc)
            return
    options = getattr(config, "html_theme_options", None) or {}
    options.setdefault("launch_buttons", {})["thebe"] = True
    config.html_theme_options = options


def config_inited_handler(app: Sphinx, config: Config) -> None:
    """``config-inited``：合并自定义配置、补齐主题默认、装配可选功能。

    触发于 conf.py 执行完毕之后、``builder-inited`` 之前；此时 ``extensions``
    已加载，动态装配新扩展必须走 ``app.setup_extension()``。
    """
    ConfigManager(app=app, config=config).apply_config()
    # 用户配置合并完成后再补默认，避免覆盖显式声明（如书系侧栏搜索按钮）
    apply_book_theme_option_defaults(config)

    app.add_config_value("use_thebe", False, "html")
    if getattr(config, "use_thebe", False):
        thebe_setup(app, config)

    app.add_config_value("version_switcher_json_url", "", "html")
    if getattr(config, "version_switcher_json_url", ""):
        version_switcher_setup(app, config)

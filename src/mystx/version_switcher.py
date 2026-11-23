"""渠道切换下拉（version switcher）配置。

为 Sphinx 主题注入版本/渠道切换下拉，并在本地预览时补上 RTD 观感样式。
三条约束由 ``tests/unit/test_version_switcher.py`` 守护：

1. 清单路径必须**相对**：pydata 对 http(s) 的 ``json_url`` 会在构建期发
   ``requests.get`` 校验，而 CI 的 harden-runner 阻断出网，绝对 URL 必然产生
   警告；首次部署前文件尚不存在，还会形成自举死锁。
2. 匹配键按构建环境判定，且必然落在清单 ``version`` 的取值域内。
3. 以 ``setdefault`` 写入，不覆盖用户显式声明。
"""
import os

from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.util import logging

logger = logging.getLogger(__name__)

#: 清单条目的 ``version`` 代号，与 ``doc/_static/switcher.json`` 一一对应；
#: 下游用自己的清单时需重新绑定。
CHANNEL_GH_PAGES = "dev"
CHANNEL_RTD = "latest"

#: 清单的默认相对路径（解析自 ``app.srcdir``，零网络依赖）。
DEFAULT_SWITCHER_JSON = "_static/switcher.json"

#: 主侧栏末端组件：pydata 默认只保留伦理广告位，覆盖时须把它带上。
DEFAULT_PRIMARY_SIDEBAR_END = ["version-switcher", "sidebar-ethical-ads"]


def resolve_version_match() -> str:
    """按构建环境返回清单里的匹配键：RTD 构建为 ``latest``，其余为 ``dev``。"""
    return CHANNEL_RTD if os.environ.get("READTHEDOCS") else CHANNEL_GH_PAGES


def sphinx_setup(app: Sphinx, config: Config) -> None:
    """注入切换下拉配置，并按需补齐本地预览的 RTD 样式。

    用户在 ``conf.py`` 或 ``_config.toml`` 中显式声明的同名键优先（``setdefault``
    语义，与 ``apply_book_theme_option_defaults`` 的约定一致）。

    Args:
        app: Sphinx 应用实例，用于注入样式与脚本。
        config: Sphinx 配置对象。
    """
    on_rtd = bool(os.environ.get("READTHEDOCS"))
    on_ci = bool(os.environ.get("GITHUB_ACTIONS"))
    json_url = getattr(config, "version_switcher_json_url", "") or DEFAULT_SWITCHER_JSON

    options = getattr(config, "html_theme_options", None) or {}
    options.setdefault(
        "switcher",
        {"json_url": json_url, "version_match": resolve_version_match()},
    )
    options.setdefault("primary_sidebar_end", list(DEFAULT_PRIMARY_SIDEBAR_END))
    config.html_theme_options = options
    logger.info("配置切换下拉: json_url=%s, version_match=%s", json_url, options["switcher"]["version_match"])

    # 仅本地预览注入 RTD 样式：RTD 与 GitHub Actions 下不注入，避免污染线上
    # 产物。这里不再引用 ``rtd-data.js``——仓库与主题目录均无该文件，而 Sphinx
    # 对缺失的 js 不告警，只会在产物里留一个 404。
    if not on_rtd and not on_ci:
        app.add_css_file(
            "https://assets.readthedocs.org/static/css/readthedocs-doc-embed.css"
        )
        app.add_css_file("https://assets.readthedocs.org/static/css/badge_only.css")
        app.add_js_file(
            "https://assets.readthedocs.org/static/javascript/readthedocs-doc-embed.js",
            priority=501,
        )

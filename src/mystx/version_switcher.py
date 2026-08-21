"""版本切换器配置模块。

为 Sphinx 主题配置 ReadTheDocs 风格的版本切换器，含本地开发环境的
dummy switcher 数据与 RTD 样式/脚本注入。
"""
import os

from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.util import logging

logger = logging.getLogger(__name__)


def sphinx_setup(app: Sphinx, config: Config) -> None:
    """配置版本切换器。

    Args:
        app: Sphinx 应用实例。
        config: Sphinx 配置对象。
    """
    logger.info("正在配置版本切换器")
    json_url = getattr(config, "version_switcher_json_url", "")
    release = config.release
    # 优先从环境变量读取版本；否则按 release 字符串推断。
    version_match = os.environ.get("READTHEDOCS_VERSION")
    if not version_match or version_match.isdigit() or version_match == "latest":
        # 本地开发环境：按 release 中的 dev/rc 标记推断版本。
        if any(marker in release for marker in ("dev", "rc")):
            version_match = "dev"
            json_url = "_static/switcher.json"
        else:
            version_match = f"v{release}"
    elif version_match == "stable":
        version_match = f"v{release}"
    logger.info(f"配置 version switcher: json_url={json_url}, version_match={version_match}")

    config["html_theme_options"].update(
        {
            "switcher": {
                "json_url": json_url,
                "version_match": version_match,
            },
            "primary_sidebar_end": ["version-switcher"],
        }
    )
    # 本地开发环境下注入 RTD 样式与 dummy 数据，模拟 ReadTheDocs 行为；
    # 在 RTD 或 GitHub Actions 下不注入，避免污染灯塔性能测试结果。
    if not os.environ.get("READTHEDOCS") and not os.environ.get("GITHUB_ACTIONS"):
        app.add_css_file(
            "https://assets.readthedocs.org/static/css/readthedocs-doc-embed.css"
        )
        app.add_css_file("https://assets.readthedocs.org/static/css/badge_only.css")

        app.add_js_file("rtd-data.js")
        app.add_js_file(
            "https://assets.readthedocs.org/static/javascript/readthedocs-doc-embed.js",
            priority=501,
        )
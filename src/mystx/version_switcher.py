"""切换下拉（通道切换器）配置模块。

为 Sphinx 主题配置版本/通道切换下拉，并负责本地预览时的 RTD 观感注入。

设计要点（三点均由 ``tests/unit/test_version_switcher.py`` 守护）：

1. **数据源用相对路径**：pydata 对 http(s) 的 ``json_url`` 会在构建期发
   ``requests.get`` 校验，读不到即 ``warning``；而本仓库 CI 用 harden-runner
   阻断出网（白名单不含 readthedocs.io），那条校验在 CI 上必然失败。
2. **匹配键按构建环境判定**，且必然落在清单的 ``version`` 取值域内。
3. **以 setdefault 语义写入**，不覆盖用户显式声明。
"""
import os

from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.util import logging

logger = logging.getLogger(__name__)

# 清单条目的 ``version`` 代号，与 ``doc/_static/switcher.json`` 一一对应。
# 下游项目若在自己的清单里用别的代号，需要重新绑定这两个模块级常量。
CHANNEL_GH_PAGES = "dev"
CHANNEL_RTD = "latest"

# 清单的**相对**路径。不要改成 http(s) 绝对 URL：
# ① pydata 对绝对 URL 在构建期发 requests.get，失败即 warning，而 CI 的
#    harden-runner 阻断出网 → 每次 CI 构建都产生一条噪声警告，且这道校验
#    永远走不到「通过」分支（守卫空转）；一旦有人给构建加 -W 或 RTD 侧开
#    fail_on_warning，构建立刻变红。
# ② 首次部署前该文件还不存在，绝对 URL 必然形成自举死锁。
# 相对路径改为读本地文件（``app.srcdir`` 下的 doc/_static/switcher.json），
# 校验照旧生效、零网络依赖，前端也按站点根解析（GH Pages 与 RTD 的
# /zh-cn/latest/ 前缀下都取得到）。
DEFAULT_SWITCHER_JSON = "_static/switcher.json"

# 主侧栏末端组件。pydata 的默认值只有后者；覆盖时把它带上，
# 否则等于顺手砍掉 RTD 侧留给项目方的伦理广告位。
DEFAULT_PRIMARY_SIDEBAR_END = ["version-switcher", "sidebar-ethical-ads"]


def resolve_version_match() -> str:
    """按**构建环境**判定当前通道，返回清单里的匹配键。

    同一份 HTML 会被部署到两条通道，页面自身认不出身在何处，
    只能由构建期环境变量决定该高亮哪一条：RTD 构建带 ``READTHEDOCS``，
    GitHub Actions 带 ``GITHUB_ACTIONS``，本地预览按 GitHub Pages 处理。

    返回值必然落在清单的 ``version`` 取值域内（有单测守护）。历史实现会
    在部分分支返回 ``f"v{release}"`` 这类清单里不存在的值，导致 pydata
    匹配不到任何条目、按钮停在服务端默认文案 "Choose version"。
    """
    return CHANNEL_RTD if os.environ.get("READTHEDOCS") else CHANNEL_GH_PAGES


def sphinx_setup(app: Sphinx, config: Config) -> None:
    """配置切换下拉。

    以 ``setdefault`` 语义写入 ``html_theme_options``——用户在 ``conf.py`` 或
    ``_config.toml`` 里的显式声明优先（与本包 ``apply_book_theme_option_defaults``
    的约定一致），绝不覆盖。

    Args:
        app: Sphinx 应用实例，用于注入本地预览所需的样式与脚本。
        config: Sphinx 配置对象。
    """
    json_url = getattr(config, "version_switcher_json_url", "") or DEFAULT_SWITCHER_JSON
    version_match = resolve_version_match()

    options = getattr(config, "html_theme_options", None) or {}
    options.setdefault("switcher", {"json_url": json_url, "version_match": version_match})
    options.setdefault("primary_sidebar_end", list(DEFAULT_PRIMARY_SIDEBAR_END))
    config.html_theme_options = options
    logger.info(f"配置切换下拉: json_url={json_url}, version_match={version_match}")

    # 本地预览时注入 RTD 的样式，贴近 Read the Docs 侧的观感；RTD 与
    # GitHub Actions 下不注入，避免污染线上产物与性能测量结果。
    # 注：原实现此处还引用了 ``rtd-data.js``，但仓库与主题目录里均无此文件，
    # 而 Sphinx 对缺失的 js **不报任何警告**（构建期静默，仅产物多一个 404），
    # 故移除该引用，不再假装能模拟 RTD 的版本数据。
    if not os.environ.get("READTHEDOCS") and not os.environ.get("GITHUB_ACTIONS"):
        app.add_css_file(
            "https://assets.readthedocs.org/static/css/readthedocs-doc-embed.css"
        )
        app.add_css_file("https://assets.readthedocs.org/static/css/badge_only.css")
        app.add_js_file(
            "https://assets.readthedocs.org/static/javascript/readthedocs-doc-embed.js",
            priority=501,
        )

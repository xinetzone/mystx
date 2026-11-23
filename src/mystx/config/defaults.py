"""构建期配置：静态默认字典与纯函数组装。

本模块不依赖任何已存在的 Sphinx 应用实例，只负责把默认字典与项目参数
合成为一份 conf.py 风格的核心配置字典；运行期对 ``Config`` 的注入见
:mod:`mystx.config.runtime`。
"""

import os
from typing import Any

from ..themes import BOOK_THEME_NAMES, DEFAULT_BOOK_THEME_OPTIONS
from ..utils import deep_merge, sitemap_enabled_by_env

DEFAULT_MYST_CONFIG: dict[str, Any] = {
    "myst_enable_extensions": [
        "dollarmath",
        "amsmath",
        "deflist",
        "colon_fence",
        "replacements",
        "substitution",
    ],
    "myst_fence_as_directive": ["mermaid"],
    "myst_heading_anchors": 3,
    "myst_commonmark_only": False,
    "myst_title_to_header": True,
}

DEFAULT_BUILD_CONFIG: dict[str, Any] = {
    "templates_path": ["_templates"],
    "exclude_patterns": [
        "_build",
        "Thumbs.db",
        ".DS_Store",
        "**.ipynb_checkpoints",
        "**/.spec/**",
        "**/.spec",
    ],
    "numfig": True,
    "nitpicky": False,
    "suppress_warnings": [
        "myst.xref_missing",
        "myst.domains",
        "ref.ref",
        "toc.external",
        "etoc.toctree",
        "ref.footnote",
        "misc.highlighting_failure",
    ],
}

DEFAULT_EXT_CONFIG: dict[str, Any] = {
    "copybutton_exclude": ".linenos, .gp",
    "copybutton_selector": ":not(.prompt) > div.highlight pre",
    "sitemap_url_scheme": "{link}",
    "extlinks": {},
}

DEFAULT_HTML_CONFIG: dict[str, Any] = {
    "html_static_path": ["_static"],
    "html_css_files": ["local.css"],
    "html_last_updated_fmt": "%Y-%m-%d, %H:%M:%S",
}


#: 文档站通用的「非身份相关」配置键：与项目名、仓库地址、源目录布局无关，
#: 可被任意 Sphinx 文档站直接合并进 ``conf.py`` 命名空间。
#:
#: 与 ``DEFAULT_*_CONFIG`` 的区别是**不参与** :func:`build_base_config` 的
#: 默认合并——这些键只在对应扩展加载时才有意义，由调用方显式取用。
DEFAULT_SITE_CONFIG: dict[str, Any] = {
    "graphviz_output_format": "svg",
    "inheritance_graph_attrs": {"rankdir": "LR", "fontsize": 14, "ratio": "compress"},
    "sitemap_locales": [None],
    "tippy_rtd_urls": [
        "https://docs.readthedocs.io/en/stable/",
        "https://www.sphinx-doc.org/zh-cn/master/",
    ],
    # 三条均为「上游实现导致、与本项目无关」的交叉引用失败，属文档站通用噪声：
    # ・autoapi 把类型注解里的 ``...`` 渲染成 ``Ellipsis`` 并按 py:class 解析，
    #   而它是内置单例、不在 intersphinx 清单中；
    # ・docutils 两符号被 myst_parser 文档工具指令引用但未纳入清单。
    # 仅精确豁免具体符号，不使用通配符压制整类 py:class 告警。
    "nitpick_ignore": [
        ("py:class", "docutils.nodes.document"),
        ("py:class", "docutils.parsers.rst.directives.body.Sidebar"),
        ("py:class", "Ellipsis"),
    ],
}


def _resolve_html_baseurl(params: dict[str, Any]) -> str | None:
    """从环境变量 / 项目参数中推断 ``html_baseurl`` 的取值（sitemap + ogp 需要）。"""
    if not sitemap_enabled_by_env():
        return None
    if os.environ.get("GITHUB_ACTIONS"):
        return os.environ.get("SITEMAP_URL_BASE", params.get("site_url"))
    return params.get("site_url") or "http://127.0.0.1:8000/"


def build_base_config(params: dict[str, Any] | None = None) -> dict[str, Any]:
    """基于默认字典 + 项目覆盖，组装出 Sphinx 所需的核心配置。

    不包含 extensions / html_theme / hooks（这些在各自模块中处理）。
    """
    params = params or {}
    merged: dict[str, Any] = {}
    merged.update(DEFAULT_BUILD_CONFIG)
    merged.update(DEFAULT_MYST_CONFIG)
    merged.update(DEFAULT_EXT_CONFIG)
    merged.update(DEFAULT_HTML_CONFIG)

    baseurl = _resolve_html_baseurl(params)
    if baseurl is not None:
        merged["html_baseurl"] = baseurl
    if "site_url" in params:
        merged["ogp_site_url"] = params["site_url"]

    return deep_merge(merged, params.get("config_override") or {})


# 书系主题名单与结构性默认均来自 ``themes``（唯一权威源）。
# pydata-sphinx-theme 0.16+ 在 builder-inited 阶段会向未声明
# ``navbar_persistent`` 的项目自动注入 ``["search-button-field"]``，
# 使顶栏出现搜索按钮；而书系主题的主侧边栏已内置同一搜索按钮
# （theme.toml sidebars 中的 search-button-field.html），两者叠加即
# 产生双搜索框。书系主题的设计意图是只保留侧边栏搜索，故在
# config-inited（早于 builder-inited）补齐空列表默认；仅在用户未
# 显式声明时生效，用户配置（conf.py / _config.toml）优先。
# 单一权威源：取值引用 ``themes.DEFAULT_BOOK_THEME_OPTIONS``，避免同一默认值
# 在本包内出现两份副本（曾因两侧各自维护而在 preset 路径与服务路径之间产生分歧）。
BOOK_THEME_OPTION_DEFAULTS: dict[str, object] = {
    "navbar_persistent": DEFAULT_BOOK_THEME_OPTIONS["navbar_persistent"],
}

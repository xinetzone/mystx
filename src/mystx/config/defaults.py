"""构建期配置：静态默认字典与纯函数组装。

本模块不依赖任何已存在的 Sphinx 应用实例，只负责把默认字典与项目参数
合成为一份 conf.py 风格的核心配置字典；运行期对 ``Config`` 的注入见
:mod:`mystx.config.runtime`。
"""

import os
from typing import Any

from ..themes import DEFAULT_BOOK_THEME_OPTIONS
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
    # 文档站（myst-nb / autoapi / docutils）链路的上游噪声，与本项目内容无关。
    # 与 ``DEFAULT_BUILD_CONFIG["suppress_warnings"]`` 分开维护：后者是 preset 的
    # 最小集合（toc/etoc 类），合并会改变 preset 行为。
    "suppress_warnings": [
        "mystnb.unknown_mime_type",
        "mystnb.mime_priority",
        "myst.xref_missing",
        "myst.domains",
        "ref.ref",
        "autoapi.python_import_resolution",
        "autoapi.not_readable",
        "docutils",
    ],
}


def _resolve_html_baseurl(params: dict[str, Any]) -> str | None:
    """preset 场景的 ``html_baseurl``：非 RTD 生效，``site_url`` 可兜底 CI 缺失值。

    与 :func:`mystx.utils.resolve_site_url` 的分工：本函数服务 ``build_base_config``
    的预置站点，允许 ``site_url`` 作为 CI 回退；站点侧则要求 CI 显式声明
    ``SITEMAP_URL_BASE``。二者共享 :func:`sitemap_enabled_by_env` 的 RTD 判据。
    """
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


# pydata 0.16+ 会在 builder-inited 注入 navbar_persistent=["search-button-field"]，
# 与书系侧栏内置搜索按钮叠加成双搜索框；故在 config-inited 以 setdefault 语义补空列表。
# 取值引用 themes.DEFAULT_BOOK_THEME_OPTIONS（唯一权威源），包内不另存副本。
BOOK_THEME_OPTION_DEFAULTS: dict[str, object] = {
    "navbar_persistent": DEFAULT_BOOK_THEME_OPTIONS["navbar_persistent"],
}

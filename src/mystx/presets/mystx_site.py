"""完整文档站预设：把站点 ``conf.py`` 中与内容无关的机制收拢为一处。

与 :mod:`mystx.presets.minimal_myst` 的分工：极简预设只装配 ``myst_parser``
与兼容钩子；本预设面向「完整 mystx 文档站」，覆盖：

* 扩展装配（包内可选清单 + 站点增量 + sitemap 条件）；
* ``DEFAULT_*_CONFIG`` 取值下放（copybutton / sitemap / graphviz / tippy /
  numfig / MyST 扩展 / nitpick 与告警基线）；
* 主题回退与可选字体增强；
* ``setup()``：文档指令注册、并行覆写与守卫、并行安全元数据。

站点身份相关数据（项目名、仓库地址、intersphinx、extlinks、autoapi 目录、
BibTeX 文件等）仍留在站点侧，避免预设对目录布局与外部链接做假设。
"""

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from sphinx.application import Sphinx

from ..config.defaults import (
    DEFAULT_BUILD_CONFIG,
    DEFAULT_EXT_CONFIG,
    DEFAULT_MYST_CONFIG,
    DEFAULT_SITE_CONFIG,
)
from ..extensions import DEFAULT_OPTIONAL_EXTENSIONS, resolve_extensions
from ..fonts import configure_optional_matplotlib_fonts
from ..myst_docs import register_docs_directives
from ..parallel import ParallelSafeOverrides, connect_parallel_guard
from ..themes import resolve_theme
from ..utils import resolve_release

#: 包内清单中默认不给完整站点的扩展：sitemap 改由 ``site_url`` 条件决定；
#: mermaid 会向每页注入引导脚本并从 CDN 拉 ESM，正文无图表时不应默认携带。
DEFAULT_EXCLUDED_OPTIONAL: tuple[str, ...] = (
    "sphinx_sitemap",
    "sphinxcontrib.mermaid",
)

#: 站点默认字体族（字体包或目录缺失时静默跳过，不影响构建）。
DEFAULT_FONT_FAMILIES: tuple[str, ...] = (
    "Maple Mono NF CN",
    "Noto Color Emoji",
)


def build_config(
    *,
    root: str | Path,
    site_url: str | None = None,
    optional_extensions: Sequence[str] = (),
    excluded_optional: Sequence[str] = DEFAULT_EXCLUDED_OPTIONAL,
    language: str = "zh_CN",
    locale_dirs: Sequence[str] = ("../locales/",),
    gettext_compact: bool = False,
    release: str | None = None,
    distribution: str = "mystx",
    version_env_var: str = "MYSTX_VERSION",
    version_fallback: str = "0.0.0",
    font_families: Sequence[str] = DEFAULT_FONT_FAMILIES,
    nitpick_ignore: Sequence[tuple[str, str]] = (),
    suppress_warnings: Sequence[str] = (),
    parallel_safe_overrides: ParallelSafeOverrides | None = None,
) -> dict[str, Any]:
    """组装完整 mystx 文档站的 conf.py 风格配置字典。

    Args:
        root: 站点根目录（``conf.py`` 所在目录的上一级），用于定位默认字体目录。
        site_url: 站点根 URL；为空时不启用 sitemap 且不写 ``html_baseurl``。
        optional_extensions: 站点在包内清单之外追加的可选扩展。
        excluded_optional: 从包内清单中剔除的扩展，默认剔除 sitemap 与 mermaid。
        language: ``language`` 取值（Sphinx 在 ``config-inited`` 前初始化 i18n）。
        locale_dirs: 翻译目录列表。
        gettext_compact: 是否合并 gettext 目录。
        release: 显式版本号；缺省时按 ``distribution`` / 环境变量 / 兜底解析。
        distribution: 用于读取已安装版本号的发行名。
        version_env_var: 读取版本号的优先环境变量。
        version_fallback: 版本号最终兜底值。
        font_families: matplotlib 字体族优先级列表。
        nitpick_ignore: 追加到包内基线之后的本站 nitpick 豁免。
        suppress_warnings: 追加到包内基线之后的本站告警抑制。
        parallel_safe_overrides: 扩展名到 ``(read_safe, write_safe)`` 的覆写表。

    Returns:
        可直接 ``globals().update(...)`` 的配置字典，含 ``setup`` 钩子。
    """
    root = Path(root)
    release = release or resolve_release(
        distribution,
        env_var=version_env_var,
        fallback=version_fallback,
    )

    excluded = frozenset(excluded_optional)
    optional = tuple(
        ext for ext in DEFAULT_OPTIONAL_EXTENSIONS if ext not in excluded
    ) + tuple(optional_extensions)

    extensions = resolve_extensions(
        required=("mystx",),
        optional=optional,
        conditional=(("sphinx_sitemap", lambda: bool(site_url)),),
    )

    theme = resolve_theme()
    configure_optional_matplotlib_fonts(
        root / "doc" / "_static" / "fonts",
        families=font_families,
    )

    overrides: Mapping[str, tuple[bool, bool]] = dict(parallel_safe_overrides or {})

    def setup(app: Sphinx) -> dict[str, Any]:
        """注册文档指令与并行守卫，并声明本扩展并行安全。"""
        register_docs_directives(app)
        connect_parallel_guard(app, overrides)
        return {
            "version": release,
            "parallel_read_safe": True,
            "parallel_write_safe": True,
        }

    return {
        "release": release,
        "version": release,
        "language": language,
        "locale_dirs": list(locale_dirs),
        "gettext_compact": gettext_compact,
        "extensions": extensions,
        "copybutton_exclude": DEFAULT_EXT_CONFIG["copybutton_exclude"],
        "copybutton_selector": DEFAULT_EXT_CONFIG["copybutton_selector"],
        "html_baseurl": site_url or "",
        "sitemap_url_scheme": "{link}" if site_url else "{lang}{version}{link}",
        "sitemap_locales": list(DEFAULT_SITE_CONFIG["sitemap_locales"]),
        "graphviz_output_format": DEFAULT_SITE_CONFIG["graphviz_output_format"],
        "inheritance_graph_attrs": dict(DEFAULT_SITE_CONFIG["inheritance_graph_attrs"]),
        "tippy_rtd_urls": list(DEFAULT_SITE_CONFIG["tippy_rtd_urls"]),
        "html_theme": theme,
        "nitpick_ignore": [*DEFAULT_SITE_CONFIG["nitpick_ignore"], *nitpick_ignore],
        "suppress_warnings": [*DEFAULT_SITE_CONFIG["suppress_warnings"], *suppress_warnings],
        "numfig": DEFAULT_BUILD_CONFIG["numfig"],
        "myst_enable_extensions": list(DEFAULT_MYST_CONFIG["myst_enable_extensions"]),
        "setup": setup,
    }

"""完整文档站预设：把站点 ``conf.py`` 中与内容无关的机制收拢为一处。

与 :mod:`mystx.presets.minimal_myst` 的分工：极简预设只装配 ``myst_parser``
与兼容钩子；本预设面向「完整 mystx 文档站」，覆盖：

* 扩展装配（包内可选清单 + 站点增量 + sitemap 条件）；
* ``DEFAULT_*_CONFIG`` 取值下放（copybutton / sitemap / graphviz / tippy /
  numfig / MyST 扩展 / nitpick 与告警基线）；
* 主题回退。

边界约定：

* :func:`build_config` 只返回取值，键集合与默认值由 :data:`SITE_CONFIG_SPEC`
  单源声明，``SiteConfig`` 是其类型镜像；
  ``setup`` 钩子随取值一起返回但不混入配置字典；
* :class:`ConfigSpec` 的 ``rebuild`` / ``types`` / ``description`` 是声明元数据，
  当前运行期不参与取值，仅用于单源维护与后续扩展化；
* :func:`apply_config` 是站点装配入口：把取值注入给定命名空间并交回
  ``setup``，conf.py 不再需要 ``globals().update`` 与临时变量；
* 字体注册是副作用，独立为 :func:`configure_site_fonts`，由站点显式调用并
  给出目录，预设不假设 ``root/doc/_static`` 布局。

站点身份相关数据（项目名、仓库地址、intersphinx、extlinks、autoapi 目录、
BibTeX 文件等）仍留在站点侧，避免预设对目录布局与外部链接做假设。
"""

from collections.abc import Callable, Iterable, Mapping, MutableMapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, NamedTuple, TypedDict, cast

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

#: 配置值的失效档，语义与 Sphinx ``add_config_value`` 的 ``rebuild`` 参数一致。
ConfigRebuild = Literal['', 'env', 'epub', 'gettext', 'html', 'applehelp', 'devhelp']


@dataclass(frozen=True, slots=True)
class _BuildContext:
    """已归一化的构建入参，供各配置键的工厂函数读取。

    入参先在此收敛为不可变形态，配置键只做取值与拷贝，不再重复计算。
    """

    release: str
    language: str
    locale_dirs: tuple[str, ...]
    gettext_compact: bool | str
    extensions: tuple[str, ...]
    site_url: str | None
    nitpick_ignore: tuple[tuple[str, str], ...]
    suppress_warnings: tuple[str, ...]


class ConfigSpec(NamedTuple):
    """一个 Sphinx 配置键的完整声明。

    ``default`` 与 Sphinx ``config._Opt.default`` 同形：可为静态值，或
    ``Callable[[_BuildContext], Any]`` 工厂；可变值（list/dict/set）必须用工厂
    返回新对象。``rebuild`` / ``types`` / ``description`` 是声明元数据，
    当前运行期不参与取值。
    """

    default: Any
    rebuild: ConfigRebuild
    types: frozenset[type]
    description: str


#: ``setup`` 钩子签名：Sphinx 在配置读入后调用，返回扩展元数据。
SetupFunction = Callable[[Sphinx], dict[str, Any]]


class SiteConfig(TypedDict):
    """预设产出的 Sphinx 配置键（不含 ``setup`` 钩子）。"""

    release: str
    version: str
    language: str
    locale_dirs: list[str]
    gettext_compact: bool
    extensions: list[str]
    copybutton_exclude: str
    copybutton_selector: str
    html_baseurl: str
    sitemap_url_scheme: str
    sitemap_locales: list[str]
    graphviz_output_format: str
    inheritance_graph_attrs: dict[str, Any]
    tippy_rtd_urls: list[str]
    html_theme: str
    nitpick_ignore: list[tuple[str, str]]
    suppress_warnings: list[str]
    numfig: bool
    myst_enable_extensions: list[str]


#: 预设配置键的唯一声明源：``SiteConfig`` 是它的类型镜像，取值由 ``default`` 生成。
#: 键集、默认值、失效档、类型与说明均在此维护，避免两处手写产生漂移。
SITE_CONFIG_SPEC: dict[str, ConfigSpec] = {
    "release": ConfigSpec(lambda ctx: ctx.release, "env", frozenset({str}), "站点版本号，写入侧栏与 sitemap。"),
    "version": ConfigSpec(lambda ctx: ctx.release, "env", frozenset({str}), "与 release 同源，满足 Sphinx 的双字段约定。"),
    "language": ConfigSpec(lambda ctx: ctx.language, "env", frozenset({str}), "文档语言；i18n 在 config-inited 之前读取。"),
    "locale_dirs": ConfigSpec(lambda ctx: list(ctx.locale_dirs), "env", frozenset({list, tuple}), "翻译目录列表。"),
    "gettext_compact": ConfigSpec(lambda ctx: ctx.gettext_compact, "gettext", frozenset({bool, str}), "是否合并 gettext 目录。"),
    "extensions": ConfigSpec(lambda ctx: list(ctx.extensions), "", frozenset({list, tuple}), "扩展清单；集合变更由 CONFIG_EXTENSIONS_CHANGED 单独检测。"),
    "copybutton_exclude": ConfigSpec(DEFAULT_EXT_CONFIG["copybutton_exclude"], "html", frozenset({str}), "copybutton 不注入按钮的元素选择器。"),
    "copybutton_selector": ConfigSpec(DEFAULT_EXT_CONFIG["copybutton_selector"], "html", frozenset({str}), "copybutton 注入按钮的代码块选择器。"),
    "html_baseurl": ConfigSpec(lambda ctx: ctx.site_url or "", "html", frozenset({str}), "站点根 URL；为空时不启用 sitemap。"),
    "sitemap_url_scheme": ConfigSpec(lambda ctx: "{link}" if ctx.site_url else "{lang}{version}{link}", "html", frozenset({str}), "sitemap 链接模板，随站点 URL 是否给定切换。"),
    "sitemap_locales": ConfigSpec(lambda _ctx: list(DEFAULT_SITE_CONFIG["sitemap_locales"]), "html", frozenset({list}), "sitemap 收录的语言列表。"),
    "graphviz_output_format": ConfigSpec(DEFAULT_SITE_CONFIG["graphviz_output_format"], "html", frozenset({str}), "Graphviz 输出格式。"),
    "inheritance_graph_attrs": ConfigSpec(lambda _ctx: dict(DEFAULT_SITE_CONFIG["inheritance_graph_attrs"]), "", frozenset({dict}), "继承图布局属性。"),
    "tippy_rtd_urls": ConfigSpec(lambda _ctx: list(DEFAULT_SITE_CONFIG["tippy_rtd_urls"]), "html", frozenset({list, tuple}), "tippy 悬浮提示的 intersphinx 来源。"),
    "html_theme": ConfigSpec(lambda _ctx: resolve_theme(), "html", frozenset({str}), "主题回退：站点未指定时由预设给出。"),
    "nitpick_ignore": ConfigSpec(lambda ctx: [*DEFAULT_SITE_CONFIG["nitpick_ignore"], *ctx.nitpick_ignore], "", frozenset({list, tuple, set}), "交叉引用豁免清单：包内基线加站点增量。"),
    "suppress_warnings": ConfigSpec(lambda ctx: [*DEFAULT_SITE_CONFIG["suppress_warnings"], *ctx.suppress_warnings], "env", frozenset({list, tuple}), "告警抑制清单：包内基线加站点增量。"),
    "numfig": ConfigSpec(DEFAULT_BUILD_CONFIG["numfig"], "env", frozenset({bool}), "图表编号开关。"),
    "myst_enable_extensions": ConfigSpec(lambda _ctx: list(DEFAULT_MYST_CONFIG["myst_enable_extensions"]), "env", frozenset({list, tuple}), "MyST 语法扩展清单。"),
}


def _check_spec_contract(spec_names: Iterable[str], mirror_names: Iterable[str]) -> None:
    """校验 spec 与类型镜像的键集一致，防止单源声明与类型契约漂移。

    模块导入期调用一次即可；不一致时抛出 :class:`RuntimeError`，消息同时列出
    缺少的键与多余的键。
    """
    declared = set(spec_names)
    mirrored = set(mirror_names)
    if declared != mirrored:
        missing = sorted(mirrored - declared)
        extra = sorted(declared - mirrored)
        raise RuntimeError(f"SITE_CONFIG_SPEC 与 SiteConfig 不一致：缺少的键 {missing}，多余的键 {extra}")


def configure_site_fonts(
    fonts_dir: str | Path,
    families: Sequence[str] = DEFAULT_FONT_FAMILIES,
) -> None:
    """注册可选 matplotlib 字体；目录或字体包缺失时仅记日志。

    字体注册带全局副作用，故与 :func:`build_config` 分离；字体目录由站点
    显式给出，避免预设对目录布局做假设。
    """
    configure_optional_matplotlib_fonts(Path(fonts_dir), families=families)


def build_config(
    *,
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
    nitpick_ignore: Sequence[tuple[str, str]] = (),
    suppress_warnings: Sequence[str] = (),
    parallel_safe_overrides: ParallelSafeOverrides | None = None,
) -> tuple[SiteConfig, SetupFunction]:
    """组装完整 mystx 文档站的 conf.py 风格配置。

    Args:
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
        nitpick_ignore: 追加到包内基线之后的本站 nitpick 豁免。
        suppress_warnings: 追加到包内基线之后的本站告警抑制。
        parallel_safe_overrides: 扩展名到 ``(read_safe, write_safe)`` 的覆写表。

    Returns:
        ``(SiteConfig, setup)``：可直接 ``globals().update(...)`` 的取值字典，
        以及需要单独挂到 ``setup`` 名字上的钩子。
    """
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

    context = _BuildContext(
        release=release,
        language=language,
        locale_dirs=tuple(locale_dirs),
        gettext_compact=gettext_compact,
        extensions=tuple(extensions),
        site_url=site_url,
        nitpick_ignore=tuple(nitpick_ignore),
        suppress_warnings=tuple(suppress_warnings),
    )
    values: dict[str, Any] = {
        name: spec.default(context) if callable(spec.default) else spec.default
        for name, spec in SITE_CONFIG_SPEC.items()
    }
    return cast(SiteConfig, values), setup


def apply_config(
    namespace: MutableMapping[str, Any],
    /,
    **options: Any,
) -> SetupFunction:
    """把站点取值注入 ``namespace``，返回 ``setup`` 钩子。

    ``options`` 与 :func:`build_config` 完全一致。取值先在局部完整组装，再一次性
    写入，避免中途异常留下半装配的命名空间。
    """
    values, setup = build_config(**options)
    namespace.update(values)
    return setup


# 键集契约在导入期校验一次：声明漂移于最早时机暴露，取值路径不再重复检查。
_check_spec_contract(SITE_CONFIG_SPEC, SiteConfig.__annotations__)

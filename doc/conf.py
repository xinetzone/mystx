#!/usr/bin/env python3
# ruff: noqa: E402
"""Sphinx 文档配置。

站点纯取值（元信息、外观、静态资源、扩展配置）在 ``doc/_config.toml``，由包内
``ConfigManager`` 在 ``config-inited`` 合并；本文件只承载 TOML 无法表达的机制：

- **加载时机**：``extensions`` 必须在 Sphinx 读取配置时即就位，``config-inited``
  之后追加不会生效；``language`` / ``locale_dirs`` / ``gettext_compact`` 同理——
  i18n 在 ``config-inited`` 之前初始化。
- **条件装配**：可选扩展按 ``has_module`` 探测跳过，缺包环境不失败。
- **环境分支**：sitemap 与 ``html_baseurl`` 依 ``READTHEDOCS`` / ``GITHUB_ACTIONS``。
- **副作用与钩子**：字体增强、文档指令注册、并行守卫。
"""
import os
import sys
from pathlib import Path

from sphinx.application import Sphinx

from mystx.config import DEFAULT_BUILD_CONFIG, DEFAULT_EXT_CONFIG, DEFAULT_MYST_CONFIG, DEFAULT_SITE_CONFIG
from mystx.extensions import DEFAULT_OPTIONAL_EXTENSIONS, resolve_extensions
from mystx.fonts import configure_optional_matplotlib_fonts
from mystx.myst_docs import register_docs_directives
from mystx.parallel import connect_parallel_guard
from mystx.themes import resolve_theme
from mystx.utils import resolve_release, resolve_site_url

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "doc"))

release = resolve_release("mystx", env_var="MYSTX_VERSION", fallback="0.0.0")
# epub3 builder 要求 version 与 copyright 非空；本包无 X.Y 短版本约定，取 release
version = release

# Sphinx 在 config-inited 之前初始化 i18n，故这三项不能走 _config.toml
language = "zh_CN"
locale_dirs = ["../locales/"]
gettext_compact = False

# ================================= 扩展装配 =================================
# 站点可选扩展 = 包内清单（剔除 sitemap，改由环境条件决定）＋ 本站增量；
# resolve_extensions 负责 has_module 探测与去重，列表顺序即加载顺序。
_SITE_OPTIONAL_EXTENSIONS = tuple(
    ext for ext in DEFAULT_OPTIONAL_EXTENSIONS if ext != "sphinx_sitemap"
) + (
    "sphinx.ext.viewcode",
    "sphinx_comments",
    "mystx.ext.gallery",
    "sphinxcontrib.bibtex",
    "autoapi.extension",
    "sphinx_examples",
    "sphinx_pyscript",
    "mystx.ext.github_readme_stats",
)

# 非 RTD 由 mystx 生成 sitemap；CI 须显式给 SITEMAP_URL_BASE（项目型 Pages 带 /mystx/ 前缀）。
# 这里用站点自己的严格判定：DEFAULT_CONDITIONAL 只看 GITHUB_ACTIONS 是否存在，
# 会放过「CI 未声明 SITEMAP_URL_BASE」的情形，把 localhost 写进线上 sitemap。
site_url = resolve_site_url(require_on_ci=True)

extensions = resolve_extensions(
    required=("mystx",),
    optional=_SITE_OPTIONAL_EXTENSIONS,
    conditional=(("sphinx_sitemap", lambda: bool(site_url)),),
)

copybutton_exclude = DEFAULT_EXT_CONFIG["copybutton_exclude"]
copybutton_selector = DEFAULT_EXT_CONFIG["copybutton_selector"]

html_baseurl = site_url or ""  # RTD 侧保持 Sphinx 默认值
sitemap_url_scheme = "{link}" if site_url else "{lang}{version}{link}"
sitemap_locales = DEFAULT_SITE_CONFIG["sitemap_locales"]

bibtex_bibfiles = ["refs.bib"]

autoapi_dirs = [str(ROOT / "src")]
autoapi_root = "autoapi"
autoapi_generate_api_docs = True

graphviz_output_format = DEFAULT_SITE_CONFIG["graphviz_output_format"]
inheritance_graph_attrs = DEFAULT_SITE_CONFIG["inheritance_graph_attrs"]
tippy_rtd_urls = DEFAULT_SITE_CONFIG["tippy_rtd_urls"]

# ================================= 主题与字体 =================================
# 回退链（mystx → sphinx_book_theme → alabaster）由包内 themes 唯一维护
html_theme = resolve_theme()
# 三重守卫（包不可用 / 目录缺失 / 调用失败）由包内实现，仅记日志
configure_optional_matplotlib_fonts(
    ROOT / "doc/_static/fonts",
    families=("Maple Mono NF CN", "Noto Color Emoji"),
)

# ================================= MyST 与告警 =================================
# 前三条为上游通用噪声（来自 DEFAULT_SITE_CONFIG）；invoke 为本项目可选依赖
nitpick_ignore = [
    *DEFAULT_SITE_CONFIG["nitpick_ignore"],
    ("py:class", "invoke.Collection"),
]

# 通用噪声来自包内 DEFAULT_SITE_CONFIG；本站只追加与 _static/switcher.json 相关的一条
suppress_warnings = [
    *DEFAULT_SITE_CONFIG["suppress_warnings"],
    "epub.unknown_project_files",  # epub 扫描 _static/switcher.json 的误报
]

numfig = DEFAULT_BUILD_CONFIG["numfig"]
# 复制一份，避免站点侧改动污染包内默认值
myst_enable_extensions = list(DEFAULT_MYST_CONFIG["myst_enable_extensions"])

intersphinx_mapping = {
    "python": ("https://docs.python.org/3.14", None),
    "sphinx": ("https://daobook.github.io/sphinx/", None),
    "pst": ("https://daobook.github.io/pydata-sphinx-theme/", None),
    "sbt": ("https://daobook.github.io/sphinx-book-theme/", None),
    "myst-nb": ("https://daobook.github.io/MyST-NB/", None),
    "myst-parser": ("https://daobook.github.io/MyST-Parser/", None),
}

extlinks = {
    "daobook": ("https://daobook.github.io/%s", "Daobook %s"),
    "xinetzone": ("https://xinetzone.github.io/%s", "xinetzone %s"),
}

nitpicky = os.environ.get("SPHINX_NITPICK", "").lower() in {"1", "true", "yes"}

# ================================= setup() =================================
# 上游未声明 parallel_{read,write}_safe 的扩展会被 Sphinx 判为串行；
# 需要并行时在此表补充扩展名（守卫实现见 mystx.parallel）。
PARALLEL_SAFE_OVERRIDES: dict[str, tuple[bool, bool]] = {}


def setup(app: Sphinx):
    """注册文档指令与并行守卫，并声明本扩展并行安全。"""
    register_docs_directives(app)
    connect_parallel_guard(app, PARALLEL_SAFE_OVERRIDES)
    return {
        "version": release,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }

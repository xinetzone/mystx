#!/usr/bin/env python3
"""Sphinx 文档配置。

站点纯取值（元信息、外观、静态资源、扩展配置）在 ``doc/_config.toml``，由包内
``ConfigManager`` 在 ``config-inited`` 合并；可复用的机制（扩展装配、默认值下放、
主题与字体、``setup`` 钩子）已萃取到 ``mystx.presets.build_mystx_site_config``。
本文件只保留本站特有内容：

- 站点根路径与 ``sys.path`` 注入；
- sitemap 的严格环境判定（CI 缺少 ``SITEMAP_URL_BASE`` 即失败）；
- 本站数据：``intersphinx_mapping`` / ``extlinks`` / autoapi / BibTeX；
- 本站增量的告警与 nitpick 豁免。
"""
import os
import sys
from pathlib import Path

from mystx.presets import build_mystx_site_config
from mystx.utils import resolve_site_url

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "doc"))

# 非 RTD 由 mystx 生成 sitemap；CI 须显式给 SITEMAP_URL_BASE（项目型 Pages 带 /mystx/ 前缀）。
# 这里用站点自己的严格判定：DEFAULT_CONDITIONAL 只看 GITHUB_ACTIONS 是否存在，
# 会放过「CI 未声明 SITEMAP_URL_BASE」的情形，把 localhost 写进线上 sitemap。
site_url = resolve_site_url(require_on_ci=True)

conf = build_mystx_site_config(
    root=ROOT,
    site_url=site_url,
    # 站点增量：包内可选清单（默认剔除 sitemap 与 mermaid）之外，本站另需 8 项。
    optional_extensions=(
        "sphinx.ext.viewcode",
        "sphinx_comments",
        "mystx.ext.gallery",
        "sphinxcontrib.bibtex",
        "autoapi.extension",
        "sphinx_examples",
        "sphinx_pyscript",
        "mystx.ext.github_readme_stats",
    ),
)

# 本站数据：预设不对目录布局与外部链接做假设
conf["autoapi_dirs"] = [str(ROOT / "src")]
conf["autoapi_root"] = "autoapi"
conf["autoapi_generate_api_docs"] = True
conf["bibtex_bibfiles"] = ["refs.bib"]
conf["intersphinx_mapping"] = {
    "python": ("https://docs.python.org/3.14", None),
    "sphinx": ("https://daobook.github.io/sphinx/", None),
    "pst": ("https://daobook.github.io/pydata-sphinx-theme/", None),
    "sbt": ("https://daobook.github.io/sphinx-book-theme/", None),
    "myst-nb": ("https://daobook.github.io/MyST-NB/", None),
    "myst-parser": ("https://daobook.github.io/MyST-Parser/", None),
}
conf["extlinks"] = {
    "daobook": ("https://daobook.github.io/%s", "Daobook %s"),
    "xinetzone": ("https://xinetzone.github.io/%s", "xinetzone %s"),
}

# 上游通用噪声已由预设下放；这里只追加本站增量
conf["nitpick_ignore"] = [
    *conf["nitpick_ignore"],
    ("py:class", "invoke.Collection"),
]
conf["suppress_warnings"] = [
    *conf["suppress_warnings"],
    "epub.unknown_project_files",  # epub 扫描 _static/switcher.json 的误报
]

conf["nitpicky"] = os.environ.get("SPHINX_NITPICK", "").lower() in {"1", "true", "yes"}

globals().update(conf)

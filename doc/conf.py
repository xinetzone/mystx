#!/usr/bin/env python3
# ruff: noqa: E402, F401
"""Sphinx 文档配置入口：引导 ``sys.path``，再按依赖顺序再导出 ``doc/_conf/`` 分组。

导入顺序即依赖顺序：``appearance`` 触发字体增强副作用；``extensions`` 依赖
``common.ROOT``；``guard.setup()`` 依赖 ``meta.release``。
站点纯取值（元信息、外观、静态资源、扩展配置）集中在 ``doc/_config.toml``，
由包内 ``ConfigManager`` 在 ``config-inited`` 合并。
"""
import sys
from pathlib import Path

_DOC_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_DOC_DIR))

from _conf.appearance import html_theme
from _conf.common import ROOT
from _conf.extensions import (
    autoapi_dirs,
    autoapi_generate_api_docs,
    autoapi_root,
    bibtex_bibfiles,
    copybutton_exclude,
    copybutton_selector,
    extensions,
    graphviz_output_format,
    html_baseurl,
    inheritance_graph_attrs,
    sitemap_locales,
    sitemap_url_scheme,
    tippy_rtd_urls,
)
from _conf.guard import connect_parallel_guard, register_docs_directives, setup
from _conf.meta import gettext_compact, language, locale_dirs, release, version
from _conf.myst import (
    extlinks,
    intersphinx_mapping,
    myst_enable_extensions,
    nitpick_ignore,
    nitpicky,
    numfig,
    suppress_warnings,
)

from mystx.config import DEFAULT_SITE_CONFIG

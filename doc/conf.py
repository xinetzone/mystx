#!/usr/bin/env python3
# ruff: noqa: E402, F401
"""Sphinx 文档配置入口。

本文件只做装配：引导 ``doc`` 进入 ``sys.path``，再按依赖顺序从 ``doc/_conf/``
再导出各分组。分组职责见 ``_conf/__init__`` 的说明。

导入顺序即依赖顺序，不可随意调整：

- ``appearance`` 触发字体增强副作用，并依赖 ``common.ROOT``；
- ``extensions`` 依赖 ``meta.project`` 与 ``common.ROOT``；
- ``guard`` 的 ``setup()`` 依赖 ``meta.release``。

``_conf`` 为普通包，``sys.path`` 引导必须先于其导入；因此本文件保留
``E402`` 文件级豁免。
"""
import sys
from pathlib import Path

_DOC_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_DOC_DIR))

from _conf.appearance import (
    exclude_patterns,
    html_copy_source,
    html_css_files,
    html_favicon,
    html_last_updated_fmt,
    html_logo,
    html_static_path,
    html_theme,
    html_title,
    templates_path,
    version_switcher_json_url,
)
from _conf.common import ROOT
from _conf.extensions import (
    autoapi_dirs,
    autoapi_generate_api_docs,
    autoapi_root,
    bibtex_bibfiles,
    comments_config,
    copybutton_exclude,
    copybutton_selector,
    extensions,
    graphviz_output_format,
    html_baseurl,
    inheritance_graph_attrs,
    ogp_site_url,
    ogp_social_cards,
    sitemap_locales,
    sitemap_url_scheme,
    tippy_rtd_urls,
)
from _conf.guard import connect_parallel_guard, register_docs_directives, setup
from _conf.meta import (
    author,
    copyright,
    gettext_compact,
    language,
    locale_dirs,
    project,
    release,
    version,
)
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

#!/usr/bin/env python3
"""Sphinx 文档配置入口。

站点取值与装配顺序整体在 ``mystx.presets.mystx_docs``；本文件负责定位仓库根
目录，并把画像逐键赋给本模块的顶层名字。

Sphinx 的契约是「conf.py 的模块命名空间即配置」：``sphinx.config`` 先 ``exec``
本文件，再以该命名空间构造 ``Config``。因此取值必须以模块级名字出现。这里选择
逐键显式赋值而不是往 ``globals()`` 里批量注入：名字在源码里可见、可检索，注入
时机与先后顺序也与普通 conf.py 完全一致，不依赖任何隐式副作用。
"""
import sys
from pathlib import Path

from mystx.presets.mystx_docs import build_config

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "doc"))

_config, setup = build_config(root=ROOT)

# 项目身份
project = _config["project"]
author = _config["author"]
copyright = _config["copyright"]
version = _config["version"]
release = _config["release"]

# 源文件与构建
exclude_patterns = _config["exclude_patterns"]
nitpicky = _config["nitpicky"]
gettext_compact = _config["gettext_compact"]

# 语言
language = _config["language"]
locale_dirs = _config["locale_dirs"]

# 主题与静态资源
html_theme = _config["html_theme"]
html_theme_options = _config["html_theme_options"]
html_static_path = _config["html_static_path"]
html_css_files = _config["html_css_files"]
templates_path = _config["templates_path"]
html_title = _config["html_title"]
html_logo = _config["html_logo"]
html_favicon = _config["html_favicon"]
html_copy_source = _config["html_copy_source"]
html_last_updated_fmt = _config["html_last_updated_fmt"]
html_baseurl = _config["html_baseurl"]

# 扩展
extensions = _config["extensions"]
myst_enable_extensions = _config["myst_enable_extensions"]
copybutton_exclude = _config["copybutton_exclude"]
copybutton_selector = _config["copybutton_selector"]
graphviz_output_format = _config["graphviz_output_format"]
numfig = _config["numfig"]
suppress_warnings = _config["suppress_warnings"]
nitpick_ignore = _config["nitpick_ignore"]

# 站点集成
comments_config = _config["comments_config"]
ogp_site_url = _config["ogp_site_url"]
ogp_social_cards = _config["ogp_social_cards"]
version_switcher_json_url = _config["version_switcher_json_url"]
sitemap_url_scheme = _config["sitemap_url_scheme"]
sitemap_locales = _config["sitemap_locales"]
tippy_rtd_urls = _config["tippy_rtd_urls"]
intersphinx_mapping = _config["intersphinx_mapping"]
extlinks = _config["extlinks"]
inheritance_graph_attrs = _config["inheritance_graph_attrs"]

# API 文档
autoapi_dirs = _config["autoapi_dirs"]
autoapi_root = _config["autoapi_root"]
autoapi_generate_api_docs = _config["autoapi_generate_api_docs"]

# 参考文献
bibtex_bibfiles = _config["bibtex_bibfiles"]

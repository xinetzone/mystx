#!/usr/bin/env python3
"""Sphinx 文档配置。

站点取值与站点机制集中在本文件：机制（扩展装配、默认值下放、主题与字体、
``setup`` 钩子）由 ``mystx.presets.build_mystx_site_config`` 提供；原
``doc/_config.toml`` 的取值已合并回此处，避免同一份站点配置在两处维护。

仍由 Sphinx 时机约束、不能交给延迟合并的项只有 ``language`` /
``locale_dirs`` / ``gettext_compact``——i18n 在 ``config-inited`` 之前初始化。
"""
import os
import sys
from pathlib import Path

from mystx.presets import build_mystx_site_config
from mystx.utils import resolve_site_url

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "doc"))

# ---- 站点元信息 ----
project = "mystx"
author = "xinetzone"
copyright = "2026, xinetzone"

# ---- 外观与静态资源 ----
# README.md 面向仓库读者，站点根入口为 index.md
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "README.md"]
html_static_path = ["_static"]
html_css_files = ["local.css", "font.css"]
html_last_updated_fmt = "%Y-%m-%d, %H:%M:%S"
templates_path = ["_templates"]
html_title = "Sphinx mystx Theme"
html_logo = "_static/images/logo.jpg"
html_favicon = "_static/images/favicon.jpg"
html_copy_source = True

# 用相对路径读本地清单：绝对 URL 会让 pydata 在构建期发请求校验，CI 阻网恒失败
version_switcher_json_url = "_static/switcher.json"

# ---- 站点专属的扩展配置 ----
comments_config = {
    "hypothesis": True,
    "utterances": {"repo": "xinetzone/mystx", "optional": "config"},
}
ogp_site_url = "https://mystx.readthedocs.io/zh-cn/latest/"
ogp_social_cards = {
    "site_url": "mystx.readthedocs.io",
    "image": "_static/images/logo.jpg",
    "font": "Maple Mono NF CN, SimHei, Microsoft YaHei",
    "line_colors": "#4078c0",
}

# ---- 主题选项 ----
html_theme_options = {
    # 公告栏
    "announcement": "欢迎使用 mystx 主题！它是现代化文档主题。",
    # 仓库相关
    "repository_url": "https://github.com/xinetzone/mystx",
    "use_repository_button": True,
    "repository_branch": "main",
    "use_source_button": True,
    "use_edit_page_button": True,
    "use_issues_button": True,
    "path_to_docs": "doc",
    # 界面布局
    "secondary_sidebar_items": "page-toc.html",
    "toc_title": "目录",
    "use_sidenotes": True,
    "show_navbar_depth": 1,
    "max_navbar_depth": 7,
    "collapse_navbar": False,
    # 按钮
    "use_download_button": True,
    "use_fullscreen_button": True,
    # 页脚
    "footer_content_items": "author.html, copyright.html, last-updated.html, extra-footer.html",
    # 图标链接
    "icon_links": [
        {
            "name": "知乎",
            "url": "https://www.zhihu.com/people/xinetzone",
            "icon": "fa-brands fa-zhihu",
            "type": "fontawesome",
        },
        {
            "name": "简书",
            "url": "https://www.jianshu.com/u/4302480a3e8e",
            "icon": "fa-solid fa-book",
            "type": "fontawesome",
        },
        {
            "name": "B站",
            "url": "https://space.bilibili.com/252192181",
            "icon": "fa-brands fa-bilibili",
            "type": "fontawesome",
        },
        {
            "name": "博客园",
            "url": "https://www.cnblogs.com/q735613050/",
            "icon": "https://xinetzone.github.io/xinetzone/media/xinetzone.jpg",
            "type": "url",
        },
        {
            "name": "领英",
            "url": "https://www.linkedin.com/in/xinet",
            "icon": "fa-brands fa-linkedin",
            "type": "fontawesome",
        },
    ],
    # 交互启动按钮
    "launch_buttons": {
        "binderhub_url": "https://mybinder.org",
        "colab_url": "https://colab.research.google.com/",
        "deepnote_url": "https://deepnote.com/",
        "notebook_interface": "jupyterlab",
        "jupyterhub_url": "https://datahub.berkeley.edu",
    },
}

# ---- 本站数据：预设不对目录布局与外部链接做假设 ----
autoapi_dirs = [str(ROOT / "src")]
autoapi_root = "autoapi"
autoapi_generate_api_docs = True
bibtex_bibfiles = ["refs.bib"]
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

# ---- 机制装配 ----
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

# 上游通用噪声已由预设下放；这里只追加本站增量
conf["nitpick_ignore"] = [
    *conf["nitpick_ignore"],
    ("py:class", "invoke.Collection"),
]
conf["suppress_warnings"] = [
    *conf["suppress_warnings"],
    "epub.unknown_project_files",  # epub 扫描 _static/switcher.json 的误报
]

nitpicky = os.environ.get("SPHINX_NITPICK", "").lower() in {"1", "true", "yes"}

globals().update(conf)

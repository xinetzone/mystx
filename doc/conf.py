#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sphinx 文档配置文件

该文件包含了 mystx 文档的所有配置项，包括项目信息、国际化设置、扩展插件、主题配置等。
"""
import os
import sys
from pathlib import Path

# 平台特定配置
if sys.platform == 'win32':
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# 设置路径
def get_project_root() -> Path:
    """获取项目根目录路径。"""
    return Path(__file__).resolve().parents[1]

ROOT = get_project_root()
try:
    from importlib.metadata import version as _pkg_version
    release = _pkg_version("mystx")
except Exception:
    release = os.environ.get("MYSTX_VERSION", "0.0.0")
_ENABLE_FONTS = os.environ.get("CONFIGURE_FONTS", "").lower() in {"1", "true", "yes"}
if _ENABLE_FONTS:
    try:
        from taolib.plot.configs.matplotlib_font import configure_matplotlib_fonts
        configure_matplotlib_fonts(
            font_directory=ROOT/'doc/_static/fonts',
            target_fonts=['Maple Mono NF CN', 'Noto Color Emoji']
        )
    except Exception:
        pass
# ================================= 项目基本信息 =================================
project = "mystx"
author = "xinetzone"
# ================================= 国际化与本地化设置 ==============================
language = 'zh_CN'       # 文档语言（中文简体）
locale_dirs = ['../locales/']  # 翻译文件存放目录
gettext_compact = False  # 是否合并子目录的PO文件（False表示不合并）

# ================================= 扩展插件配置 =================================
import importlib.util as _ilut
def _has(mod: str) -> bool:
    return _ilut.find_spec(mod) is not None
extensions = [e for e in ['mystx'] if _has(e)]

# ================================= 文档构建配置 =================================
# 排除文件和目录模式
exclude_patterns = [
    "_build",      # 构建输出目录
    "Thumbs.db",   # 缩略图数据库
    ".DS_Store",    # macOS 系统文件
]

# 静态资源目录，用于存放CSS、JavaScript、图片等
html_static_path = ["_static"]
html_css_files = ["local.css", "font.css"]
# 文档的最后更新时间格式
html_last_updated_fmt = '%Y-%m-%d, %H:%M:%S'

# ================================= 主题与外观配置 ================================
if _has('mystx'):
    html_theme = 'mystx'
elif _has('sphinx_book_theme'):
    html_theme = 'sphinx_book_theme'
else:
    html_theme = 'alabaster'
html_title = "Sphinx mystx Theme"  # 文档标题
html_logo = "_static/images/logo.jpg"  # 文档logo
html_favicon = "_static/images/favicon.jpg"  # 文档favicon
html_copy_source = True  # 是否在文档中包含源文件链接

# ================================= thebe 交互式功能配置 =================================
# use_thebe = True  # 是否开启Thebe功能（默认关闭）
# thebe_config = {
#     "repository_url": f"https://github.com/xinetzone/{project}",
#     "repository_branch": "main",
#     "selector": "div.highlight",
#     # "selector": ".thebe",
#     # "selector_input": "",
#     # "selector_output": "",
#     # "codemirror-theme": "blackboard",  # Doesn't currently work
#     # "always_load": True,  # To load thebe on every page
# }

# ================================= 版本切换器配置 =================================
version_switcher_json_url = "https://mystx.readthedocs.io/zh-cn/latest/_static/switcher.json"
# ================================= 可选插件 =================================
extensions.extend([
    "sphinx_design",                # 增强设计元素
    "sphinx.ext.viewcode",          # 添加到高亮源代码的链接
    "sphinx.ext.intersphinx",       # 链接到其他文档
    "sphinx_copybutton",            # 为代码块添加复制按钮
    "sphinx_comments",              # 添加评论和注释功能
    "_ext.gallery_directive",       # 自定义画廊指令
])
# =============================================================================
# 可选功能配置
# =============================================================================
# 1. 代码复制按钮配置
copybutton_exclude = '.linenos, .gp'  # 排除行号和提示符
# 选择器配置，避免复制按钮出现在笔记本单元格编号上
copybutton_selector = ":not(.prompt) > div.highlight pre"
# 2. 评论系统配置
comments_config = {
   "hypothesis": True,  # 启用 Hypothesis 注释
   "utterances": {
      "repo": "xinetzone/mystx",
      "optional": "config",
   }  # 启用 Utterances 评论
}

# ReadTheDocs has its own way of generating sitemaps, etc.
sitemap_url_scheme = "{lang}{version}{link}"
if os.environ.get("GITHUB_ACTIONS"):
    html_baseurl = os.environ.get("SITEMAP_URL_BASE", "https://xinetzone.github.io/")
elif not os.environ.get("READTHEDOCS"):
    extensions += ["sphinx_sitemap"]
    html_baseurl = os.environ.get("SITEMAP_URL_BASE", "http://127.0.0.1:8000/")
    sitemap_url_scheme = "{link}"

sitemap_locales = [None]  # 语言列表

# 3. 参考文献配置
extensions.append('sphinxcontrib.bibtex')
bibtex_bibfiles = ['refs.bib']  # BibTeX 文件路径

# 4. API 文档自动生成
extensions.append("autoapi.extension")
autoapi_dirs = [str(ROOT/"src")]  # 源代码目录
autoapi_root = "autoapi"  # API 文档输出目录
autoapi_generate_api_docs = True  # 启用 API 文档生成

# 5. 图表生成配置
extensions.append("sphinx.ext.graphviz")
graphviz_output_format = "svg"  # 输出格式
inheritance_graph_attrs = {
    "rankdir": "LR",  # 图表方向：从左到右
    "fontsize": 14,  # 字体大小
    "ratio": "compress",  # 压缩比例
}

# 6. GitHub 贡献者显示
extensions.append('sphinx_contributors')

# 8. 社交媒体预览元数据
extensions.append("sphinxext.opengraph")
ogp_site_url = f"https://{project}.readthedocs.io/zh-cn/latest/"
ogp_social_cards = {
    "site_url": f"{project}.readthedocs.io",
    "image": "_static/images/logo.jpg",
    "font": "Maple Mono NF CN",  # 支持中文字体
    "line_colors": "#4078c0",
}

# 10. 丰富的悬停提示
extensions.append("sphinx_tippy")
tippy_rtd_urls = [
    "https://docs.readthedocs.io/en/stable/",
    "https://www.sphinx-doc.org/zh-cn/master/",
]

# =============================================================================
# 高级配置
# =============================================================================
# 忽略特定的 Nitpick 警告
nitpick_ignore = [
    ("py:class", "docutils.nodes.document"),
    ("py:class", "docutils.parsers.rst.directives.body.Sidebar"),
]

# 抑制特定警告
suppress_warnings = [
    "mystnb.unknown_mime_type", "mystnb.mime_priority",
    "myst.xref_missing", "myst.domains",
    "ref.ref",
    "autoapi.python_import_resolution", "autoapi.not_readable",
]

# 启用编号功能
numfig = True

# MyST 扩展配置
myst_enable_extensions = [
    "dollarmath",  # 数学公式支持
    "amsmath",  # 高级数学支持
    "deflist",  # 定义列表
    "colon_fence",  # 冒号分隔的围栏
    "replacements",  # 文本替换
    "substitution",  # 变量替换
]

# 自定义侧边栏
html_sidebars = {
    "reference/blog/*": [
        "navbar-logo.html",
        "search-field.html",
        "ablog/postcard.html",
        "ablog/recentposts.html",
        "ablog/tagcloud.html",
        "ablog/categories.html",
        "ablog/archives.html",
        "sbt-sidebar-nav.html",
    ]
}

extensions.extend([
    "sphinx.ext.intersphinx",  # 跨文档链接
    "sphinx.ext.extlinks",  # 短链接支持
    "sphinx_examples",  # 示例功能
])
# 交叉引用配置
intersphinx_mapping = {
    "python": ("https://docs.python.org/3.12", None),
    "sphinx": ("https://daobook.github.io/sphinx/", None),
    "pst": ("https://daobook.github.io/pydata-sphinx-theme/", None),
    "sbt": ("https://daobook.github.io/sphinx-book-theme/", None),
    "myst-nb": ("https://daobook.github.io/MyST-NB/", None),
    "myst-parser": ("https://daobook.github.io/MyST-Parser/", None),
}

# 短链接配置
extlinks = {
    'daobook': ('https://daobook.github.io/%s', 'Daobook %s'),
    'xinetzone': ('https://xinetzone.github.io/%s', 'xinetzone %s'),
}

# ========================== 可选功能配置 ==========================
# PyScript 插件
extensions.append("sphinx_pyscript")

# GitHub 统计卡片插件
extensions.append("mystx.ext.github_readme_stats")

def setup(app: Sphinx):
    """Add functions to the Sphinx setup."""
    from myst_parser._docs import (
        DirectiveDoc,
        DocutilsCliHelpDirective,
        MystAdmonitionDirective,
        MystConfigDirective,
        MystExampleDirective,
        MystLexer,
        MystToHTMLDirective,
        MystWarningsDirective,
        NumberSections,
        StripUnsupportedLatex,
    )

    app.add_directive("myst-config", MystConfigDirective)
    app.add_directive("docutils-cli-help", DocutilsCliHelpDirective)
    app.add_directive("doc-directive", DirectiveDoc)
    app.add_directive("myst-warnings", MystWarningsDirective)
    app.add_directive("myst-example", MystExampleDirective)
    app.add_directive("myst-admonitions", MystAdmonitionDirective)
    app.add_directive("myst-to-html", MystToHTMLDirective)
    app.add_post_transform(StripUnsupportedLatex)
    app.add_post_transform(NumberSections)
    app.add_lexer("myst", MystLexer)
nitpicky = os.environ.get("SPHINX_NITPICK", "").lower() in {"1", "true", "yes"}
templates_path = ["_templates"]

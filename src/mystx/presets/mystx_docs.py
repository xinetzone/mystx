"""本项目文档站的站点画像：原 ``doc/conf.py`` 的取值与装配顺序集中于此。

边界：

* 本模块是**具体站点**的画像（项目身份、主题选项、外部链接），不是库的通用
  默认值；通用机制在 :mod:`mystx.presets.mystx_site`；
* 根目录由调用方传入——``conf.py`` 知道自己在仓库里的位置，安装后的包不知道；
* :func:`configure` 仍遵守 ``mystx_site`` 的约定：取值注入命名空间，``setup``
  钩子单独返回。

仍由 Sphinx 时机约束、不能交给延迟合并的项只有 ``language`` /
``locale_dirs`` / ``gettext_compact``——i18n 在 ``config-inited`` 之前初始化。
"""

import copy
import os
from collections.abc import MutableMapping
from pathlib import Path
from typing import Any

from ..utils import resolve_site_url
from .mystx_site import SetupFunction, apply_config, configure_site_fonts

PROJECT = "mystx"
AUTHOR = "xinetzone"
COPYRIGHT = "2026, xinetzone"

# README.md 面向仓库读者，站点根入口为 index.md
EXCLUDE_PATTERNS = ["_build", "Thumbs.db", ".DS_Store", "README.md"]
HTML_STATIC_PATH = ["_static"]
HTML_CSS_FILES = ["local.css", "font.css"]
HTML_LAST_UPDATED_FMT = "%Y-%m-%d, %H:%M:%S"
TEMPLATES_PATH = ["_templates"]
HTML_TITLE = "Sphinx mystx Theme"
HTML_LOGO = "_static/images/logo.jpg"
HTML_FAVICON = "_static/images/favicon.jpg"

# 用相对路径读本地清单：绝对 URL 会让 pydata 在构建期发请求校验，CI 阻网恒失败
VERSION_SWITCHER_JSON_URL = "_static/switcher.json"

COMMENTS_CONFIG = {
    "hypothesis": True,
    "utterances": {"repo": "xinetzone/mystx", "optional": "config"},
}
OGP_SITE_URL = "https://mystx.readthedocs.io/zh-cn/latest/"
OGP_SOCIAL_CARDS = {
    "site_url": "mystx.readthedocs.io",
    "image": "_static/images/logo.jpg",
    "font": "Maple Mono NF CN, SimHei, Microsoft YaHei",
    "line_colors": "#4078c0",
}

THEME_OPTIONS = {
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

BIBTEX_BIBFILES = ["refs.bib"]
INTERSPHINX_MAPPING = {
    # 第二条给本地清单文件名（相对 srcdir）：docs.python.org 的 TLS 握手实测约 40s，
    # 取回一次后落盘复用；Python 版本升级时重新下载 _inv/python.inv
    "python": ("https://docs.python.org/3.14", "_inv/python.inv"),
    "sphinx": ("https://daobook.github.io/sphinx/", None),
    "pst": ("https://daobook.github.io/pydata-sphinx-theme/", None),
    "sbt": ("https://daobook.github.io/sphinx-book-theme/", None),
    "myst-nb": ("https://daobook.github.io/MyST-NB/", None),
    "myst-parser": ("https://daobook.github.io/MyST-Parser/", None),
}
EXTLINKS = {
    "daobook": ("https://daobook.github.io/%s", "Daobook %s"),
    "xinetzone": ("https://xinetzone.github.io/%s", "xinetzone %s"),
}

# 站点增量：包内可选清单（默认剔除 sitemap 与 mermaid）之外，本站另需 8 项
OPTIONAL_EXTENSIONS = (
    "sphinx.ext.viewcode",
    "sphinx_comments",
    "mystx.ext.gallery",
    "sphinxcontrib.bibtex",
    "autoapi.extension",
    "sphinx_examples",
    "sphinx_pyscript",
    "mystx.ext.github_readme_stats",
)
# 上游通用噪声由预设下放，这里只追加本站增量
NITPICK_IGNORE = (("py:class", "invoke.Collection"),)
# epub 扫描 _static/switcher.json 的误报
SUPPRESS_WARNINGS = ("epub.unknown_project_files",)


def configure(namespace: MutableMapping[str, Any], *, root: str | Path) -> SetupFunction:
    """把本项目文档站的全部取值注入 ``namespace``，返回 ``setup`` 钩子。

    ``root`` 是仓库根目录：``autoapi_dirs`` 与字体目录都相对它定位，避免包内
    猜测站点布局。
    """
    root = Path(root)
    namespace.update(
        {
            "project": PROJECT,
            "author": AUTHOR,
            "copyright": COPYRIGHT,
            # 取值注入副本：扩展（如版本切换器）会就地改写这些字典/列表，
            # 共享模块常量会让同进程的第二次装配看到上一次的副作用。
            "exclude_patterns": list(EXCLUDE_PATTERNS),
            "html_static_path": list(HTML_STATIC_PATH),
            "html_css_files": list(HTML_CSS_FILES),
            "html_last_updated_fmt": HTML_LAST_UPDATED_FMT,
            "templates_path": list(TEMPLATES_PATH),
            "html_title": HTML_TITLE,
            "html_logo": HTML_LOGO,
            "html_favicon": HTML_FAVICON,
            "html_copy_source": True,
            "version_switcher_json_url": VERSION_SWITCHER_JSON_URL,
            "comments_config": copy.deepcopy(COMMENTS_CONFIG),
            "ogp_site_url": OGP_SITE_URL,
            "ogp_social_cards": copy.deepcopy(OGP_SOCIAL_CARDS),
            "html_theme_options": copy.deepcopy(THEME_OPTIONS),
            "autoapi_dirs": [str(root / "src")],
            "autoapi_root": "autoapi",
            "autoapi_generate_api_docs": True,
            "bibtex_bibfiles": list(BIBTEX_BIBFILES),
            "intersphinx_mapping": copy.deepcopy(INTERSPHINX_MAPPING),
            "extlinks": copy.deepcopy(EXTLINKS),
            "nitpicky": os.environ.get("SPHINX_NITPICK", "").lower() in {"1", "true", "yes"},
        }
    )

    # 字体注册是副作用，显式调用；字体目录由站点给出，预设不假设布局
    configure_site_fonts(root / "doc" / "_static" / "fonts")

    # 非 RTD 由 mystx 生成 sitemap；CI 须显式给 SITEMAP_URL_BASE（项目型 Pages 带 /mystx/ 前缀）。
    # 这里用站点自己的严格判定：DEFAULT_CONDITIONAL 只看 GITHUB_ACTIONS 是否存在，
    # 会放过「CI 未声明 SITEMAP_URL_BASE」的情形，把 localhost 写进线上 sitemap。
    return apply_config(
        namespace,
        site_url=resolve_site_url(require_on_ci=True),
        optional_extensions=OPTIONAL_EXTENSIONS,
        nitpick_ignore=NITPICK_IGNORE,
        suppress_warnings=SUPPRESS_WARNINGS,
    )

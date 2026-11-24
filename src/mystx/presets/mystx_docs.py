"""本项目文档站的站点画像：原 ``doc/conf.py`` 的取值与装配顺序集中于此。

边界：

* 本模块是**具体站点**的画像（项目身份、主题选项、外部链接），不是库的通用
  默认值；通用机制在 :mod:`mystx.presets.mystx_site`；
* 根目录由调用方传入——``conf.py`` 知道自己在仓库里的位置，安装后的包不知道；
* :func:`build_config` 只产出取值表与 ``setup`` 钩子，不接收命名空间：写入
  ``conf.py`` 是站点自己的契约（Sphinx 以 conf.py 的模块命名空间构造
  ``Config``）。

仍由 Sphinx 时机约束、不能交给 ``config-inited`` 的项只有 ``extensions``
（加载扩展）与 ``language`` / ``locale_dirs`` / ``gettext_compact``（i18n 在
``config-inited`` 之前初始化）。

本模块只服务这一个站点，每个取值都只用一次，因此不设模块级常量：一律写在
:func:`build_config` 的构造处。每次调用都得到全新对象，扩展就地改写字典或
列表时不会波及同进程的另一份装配。
"""

import os
from pathlib import Path
from typing import Any

from ..utils import resolve_site_url
from .mystx_site import SetupFunction, configure_site_fonts
from .mystx_site import build_config as build_site_config


def build_config(*, root: str | Path) -> tuple[dict[str, Any], SetupFunction]:
    """返回本项目文档站的取值表与 ``setup`` 钩子，不写调用方命名空间。

    ``root`` 是仓库根目录：``autoapi_dirs`` 与字体目录都相对它定位，避免包内
    猜测站点布局。取值全部是本函数内新建的字面量，调用方或扩展就地改写时不会
    影响另一次装配。

    写入命名空间由 ``conf.py`` 负责：Sphinx 先 ``exec`` conf.py，再以其模块
    命名空间构造 ``Config``（``sphinx.config.eval_config_file``），注入点是
    站点自己的契约，库只产出取值。唯一副作用是注册站点字体。
    """
    root = Path(root)
    values: dict[str, Any] = {
        "project": "mystx",
        "author": "xinetzone",
        "copyright": "2026, xinetzone",
        # README.md 面向仓库读者，站点根入口为 index.md
        "exclude_patterns": ["_build", "Thumbs.db", ".DS_Store", "README.md"],
        "html_static_path": ["_static"],
        "html_css_files": ["local.css", "font.css"],
        "html_last_updated_fmt": "%Y-%m-%d, %H:%M:%S",
        "templates_path": ["_templates"],
        "html_title": "Sphinx mystx Theme",
        "html_logo": "_static/images/logo.jpg",
        "html_favicon": "_static/images/favicon.jpg",
        "html_copy_source": True,
        # 用相对路径读本地清单：绝对 URL 会让 pydata 在构建期发请求校验，CI 阻网恒失败
        "version_switcher_json_url": "_static/switcher.json",
        "comments_config": {
            "hypothesis": True,
            "utterances": {"repo": "xinetzone/mystx", "optional": "config"},
        },
        "ogp_site_url": "https://mystx.readthedocs.io/zh-cn/latest/",
        "ogp_social_cards": {
            "site_url": "mystx.readthedocs.io",
            "image": "_static/images/logo.jpg",
            "font": "Maple Mono NF CN, SimHei, Microsoft YaHei",
            "line_colors": "#4078c0",
        },
        "html_theme_options": {
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
        },
        "autoapi_dirs": [str(root / "src")],
        "autoapi_root": "autoapi",
        "autoapi_generate_api_docs": True,
        "bibtex_bibfiles": ["refs.bib"],
        "intersphinx_mapping": {
            # 第二条给本地清单文件名（相对 srcdir）：docs.python.org 的 TLS 握手实测约 40s，
            # 取回一次后落盘复用；Python 版本升级时重新下载 _inv/python.inv
            "python": ("https://docs.python.org/3.14", "_inv/python.inv"),
            "sphinx": ("https://daobook.github.io/sphinx/", None),
            "pst": ("https://daobook.github.io/pydata-sphinx-theme/", None),
            "sbt": ("https://daobook.github.io/sphinx-book-theme/", None),
            "myst-nb": ("https://daobook.github.io/MyST-NB/", None),
            "myst-parser": ("https://daobook.github.io/MyST-Parser/", None),
        },
        "extlinks": {
            "daobook": ("https://daobook.github.io/%s", "Daobook %s"),
            "xinetzone": ("https://xinetzone.github.io/%s", "xinetzone %s"),
        },
        "nitpicky": os.environ.get("SPHINX_NITPICK", "").lower() in {"1", "true", "yes"},
    }

    # 字体注册是副作用，显式调用；字体目录由站点给出，预设不假设布局
    configure_site_fonts(root / "doc" / "_static" / "fonts")

    # 非 RTD 由 mystx 生成 sitemap；CI 须显式给 SITEMAP_URL_BASE（项目型 Pages 带 /mystx/ 前缀）。
    # 这里用站点自己的严格判定：DEFAULT_CONDITIONAL 只看 GITHUB_ACTIONS 是否存在，
    # 会放过「CI 未声明 SITEMAP_URL_BASE」的情形，把 localhost 写进线上 sitemap。
    site_values, setup = build_site_config(
        site_url=resolve_site_url(require_on_ci=True),
        optional_extensions=(
            # 站点增量：包内可选清单（默认剔除 sitemap 与 mermaid）之外，本站另需 8 项
            "sphinx.ext.viewcode",
            "sphinx_comments",
            "mystx.ext.gallery",
            "sphinxcontrib.bibtex",
            "autoapi.extension",
            "sphinx_examples",
            "sphinx_pyscript",
            "mystx.ext.github_readme_stats",
        ),
        # 上游通用噪声由预设下放，这里只追加本站增量
        nitpick_ignore=(("py:class", "invoke.Collection"),),
        # epub 扫描 _static/switcher.json 的误报
        suppress_warnings=("epub.unknown_project_files",),
    )
    # 通用站点键先落、机制取值后覆盖，与原先「两次 update」的优先级一致
    return {**values, **site_values}, setup

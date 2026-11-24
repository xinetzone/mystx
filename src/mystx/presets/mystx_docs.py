"""本项目文档站的站点画像：原 ``doc/conf.py`` 的取值与装配顺序集中于此。

边界：

* 本模块是**具体站点**的画像（主题选项、外部链接、OGP 与文档工具取值），不是
  库的通用默认值；通用机制与站点装配在 :mod:`mystx.presets.mystx_site`，装配
  调用由 ``conf.py`` 发起；
* 根目录由调用方传入——``conf.py`` 知道自己在仓库里的位置，安装后的包不知道；
* 站点身份与品牌资源（``project`` / ``author`` / ``copyright`` / ``html_title`` /
  ``html_logo`` / ``html_favicon``）不在这里：它们属于站点门面，由 ``conf.py``
  直接持有，画像只管可复用的取值；
* :func:`build_config` 只产出取值表，不接收命名空间、不持有 ``setup``：写入
  ``conf.py`` 是站点自己的契约（Sphinx 以 conf.py 的模块命名空间构造
  ``Config``）。

仍由 Sphinx 时机约束、不能交给 ``config-inited`` 的项只有 ``extensions``
（加载扩展）与 ``language`` / ``locale_dirs`` / ``gettext_compact``（i18n 在
``config-inited`` 之前初始化）。

本模块只服务这一个站点，每个取值都只用一次，因此不设模块级常量：取值写在
:func:`build_config` 及其局部辅助函数的构造处。每次调用都得到全新对象，扩展
就地改写字典或列表时不会波及同进程的另一份装配。
"""

import os
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from .mystx_site import configure_site_fonts

#: 社交卡片按序尝试的字体族：取构建机上第一个已安装者，全部缺失时回退
#: sphinxext-opengraph 内置的 Roboto Flex。
OGP_FONT_CANDIDATES: tuple[str, ...] = (
    "Maple Mono NF CN",
    "SimHei",
    "Microsoft YaHei",
    "Noto Sans CJK SC",
    "WenQuanYi Zen Hei",
)


def _available_ogp_font(
    candidates: Sequence[str] = OGP_FONT_CANDIDATES,
) -> str | None:
    """返回构建机已安装的首个候选字体族，无法探测或全部缺失时返回 ``None``。

    matplotlib 会对 ``font.family`` 里每个未安装的字体族在每次文字排版时输出
    ``findfont: Font family ... not found``。把整串候选直接交给 opengraph，
    会让缺字体的机器在逐页生成社交卡片时刷出成千上万行日志；这里先查
    matplotlib 已索引的字体族，只传真正可用的一项。
    """
    try:
        from matplotlib import font_manager
    except ImportError:
        return None
    installed = {font.name for font in font_manager.fontManager.ttflist}
    return next((name for name in candidates if name in installed), None)


def _ogp_values() -> dict[str, Any]:
    """本站的 Open Graph 取值：站点地址与社交卡片参数。

    卡片字体只取本机真正安装的族；全部缺失时不设 ``font``，交给 opengraph
    内置字体，避免 matplotlib 逐页生成卡片时对每个缺失族输出 findfont 告警。
    """
    social_cards: dict[str, Any] = {
        "site_url": "mystx.readthedocs.io",
        "image": "_static/images/logo.jpg",
        "line_colors": "#4078c0",
    }
    if (ogp_font := _available_ogp_font()) is not None:
        social_cards["font"] = ogp_font
    return {
        "ogp_site_url": "https://mystx.readthedocs.io/zh-cn/latest/",
        "ogp_social_cards": social_cards,
    }


def build_config(*, root: str | Path) -> dict[str, Any]:
    """返回本项目文档站的取值表，不写调用方命名空间、不持有 ``setup``。

    ``root`` 是仓库根目录：``autoapi_dirs`` 与字体目录都相对它定位，避免包内
    猜测站点布局。取值全部在函数内新建，调用方或扩展就地改写时不会影响另一次
    装配。

    站点机制（扩展清单、sitemap、并行守卫）由 ``conf.py`` 调用
    :func:`mystx.presets.mystx_site.build_config` 装配后合并；本函数只产出
    画像取值。唯一副作用是注册站点字体。
    """
    root = Path(root)
    values: dict[str, Any] = {
        **_ogp_values(),
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
    return values

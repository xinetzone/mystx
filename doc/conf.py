#!/usr/bin/env python3
"""Sphinx 文档配置入口。

本站的取值都在本模块显式声明：Sphinx 以 conf.py 的模块命名空间构造
``Config``，模块执行完毕时其余键已就位，构建期各消费者读到的就是这里的值。

唯一的例外是 ``html_theme_options``：这里只写覆盖项，主题默认值由 ``mystx``
扩展在 ``config-inited`` 阶段按 ``setdefault`` 补齐。原因是书系主题的 Python
侧只读配置层，站点没有理由重复抄写一份主题默认值。

``setup`` 只负责两件机制性工作：注册 mystx 的文档指令、连接并行读守卫，并
声明本扩展并行安全。

包内仍提供 ``mystx.presets.assemble_site_config`` 供其他站点批量装配，本站
选择逐项显式声明，便于直接看出每条配置的实际取值。
"""

import sys
from pathlib import Path
from typing import Any

from mystx.fonts import first_installed_family as _first_installed_family
from mystx.myst_docs import register_docs_directives as _register_docs_directives
from mystx.parallel import connect_parallel_guard as _connect_parallel_guard
from mystx.presets.xinetzone import icon_links as _icon_links
from mystx.presets.xinetzone import intersphinx_mapping as _intersphinx_mapping
from mystx.utils import resolve_release as _resolve_release
from mystx.utils import resolve_site_url as _resolve_site_url

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "doc"))

# 站点地址：本站严格判定——CI 必须显式给 SITEMAP_URL_BASE（项目型 Pages 带 /mystx/ 前缀）；
# DEFAULT_CONDITIONAL 只看 GITHUB_ACTIONS 是否存在，会放过未声明的情形，把 localhost 写进线上 sitemap
_site_url = _resolve_site_url(require_on_ci=True)

# 版本号：分发包元数据 → 环境变量 → 兜底，三级回退
release = _resolve_release("mystx", env_var="MYSTX_VERSION", fallback="0.0.0")
version = release

# 站点身份：只有这一个站点，直接写在门面上
project = "mystx"
author = "xinetzone"
copyright = "2026, xinetzone"

# 品牌资源：相对 confdir 的真实文件，由 Sphinx 校验并复制
html_title = "Sphinx mystx Theme"
html_logo = "_static/images/logo.jpg"
html_favicon = "_static/images/favicon.jpg"

# 主题与主题选项：这里只写本站的覆盖项，主题默认值由 ``mystx`` 在
# ``config-inited`` 阶段补齐——基主题的 Python 侧只读 ``html_theme_options``，
# 不读 ``theme.toml``，故默认值不能只存在于主题文件里
html_theme = "mystx"
html_theme_options = {
    # 公告栏
    "announcement": "欢迎使用 mystx 主题！它是现代化文档主题。",
    # 仓库地址（其余仓库按钮、布局与页脚取主题默认值）
    "repository_url": "https://github.com/xinetzone/mystx",
    # 图标链接（作者个人账号，取值在 mystx.presets.xinetzone）
    "icon_links": _icon_links(),
    # 交互启动按钮
    "launch_buttons": {
        "binderhub_url": "https://mybinder.org",
        "colab_url": "https://colab.research.google.com/",
        "deepnote_url": "https://deepnote.com/",
        "notebook_interface": "jupyterlab",
        "jupyterhub_url": "https://datahub.berkeley.edu",
    },
}

# 文档工具取值
autoapi_dirs = [str(ROOT / "src")]
autoapi_root = "autoapi"
autoapi_generate_api_docs = True
bibtex_bibfiles = ["refs.bib"]
# 作者个人的 intersphinx 源表（含本地清单缓存偏好）
intersphinx_mapping = _intersphinx_mapping()
extlinks = {
    "daobook": ("https://daobook.github.io/%s", "Daobook %s"),
    "xinetzone": ("https://xinetzone.github.io/%s", "xinetzone %s"),
}
nitpicky = False

# 构建参数
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_static_path = ["_static"]  # 自定义静态文件（样式表、脚本、图片）的源目录
html_last_updated_fmt = "%Y-%m-%d, %H:%M:%S"
numfig = True
graphviz_output_format = "svg"
inheritance_graph_attrs = {"rankdir": "LR", "fontsize": 14, "ratio": "compress"}
tippy_rtd_urls = [
    "https://docs.readthedocs.io/en/stable/",
    "https://www.sphinx-doc.org/zh-cn/master/",
]

# 站点行为开关：源文件链接、版本切换清单、评论组件
html_copy_source = True
# 用相对路径读本地清单：绝对 URL 会让 pydata 在构建期发请求校验，CI 阻网恒失败
version_switcher_json_url = "_static/switcher.json"
comments_config = {
    "hypothesis": True,
    "utterances": {"repo": "xinetzone/mystx", "optional": "config"},
}

# sitemap：仅在站点地址确定时启用
html_baseurl = _site_url or ""
sitemap_url_scheme = "{link}" if _site_url else "{lang}{version}{link}"
sitemap_locales = [None]

# 告警与交叉引用豁免：前四条为上游实现导致的本站噪声，末条为 invoke 类型缺陷
nitpick_ignore = [
    ("py:class", "docutils.nodes.document"),
    ("py:class", "docutils.parsers.rst.directives.body.Sidebar"),
    ("py:class", "Ellipsis"),
    ("py:class", "invoke.Collection"),
]
suppress_warnings = [
    "mystnb.unknown_mime_type",
    "mystnb.mime_priority",
    "myst.xref_missing",
    "myst.domains",
    "ref.ref",
    "autoapi.python_import_resolution",
    "autoapi.not_readable",
    "docutils",
    "epub.unknown_project_files",
]

# 代码块复制按钮
copybutton_exclude = ".linenos, .gp"
copybutton_selector = ":not(.prompt) > div.highlight pre"

# MyST 语法扩展
myst_enable_extensions = [
    "dollarmath",
    "amsmath",
    "deflist",
    "colon_fence",
    "replacements",
    "substitution",
]

# Open Graph：站点地址与社交卡片
ogp_site_url = "https://mystx.readthedocs.io/zh-cn/latest/"
# 社交卡片；字体取包内默认的 CJK 回退链（见 mystx.fonts），只传本机已装族
ogp_social_cards: dict[str, Any] = {
    "site_url": "mystx.readthedocs.io",
    "image": "_static/images/logo.jpg",
    "line_colors": "#4078c0",
}
if (_ogp_font := _first_installed_family()) is not None:
    ogp_social_cards["font"] = _ogp_font

# 扩展清单：Sphinx 在 config-inited 之前加载，必须在模块层可见
extensions = [
    "mystx",
    "sphinx_design",
    "sphinx_copybutton",
    "sphinx_tippy",
    "sphinx.ext.intersphinx",
    "sphinx.ext.extlinks",
    "sphinx.ext.graphviz",
    "sphinx_contributors",
    "sphinxext.opengraph",
    "sphinx.ext.viewcode",
    "sphinx_comments",
    "mystx.ext.gallery",
    "sphinxcontrib.bibtex",
    "autoapi.extension",
    "sphinx_examples",
    "sphinx_pyscript",
    "mystx.ext.github_readme_stats",
]
if _site_url:
    extensions.append("sphinx_sitemap")

# i18n：Sphinx 在 config-inited 之前初始化翻译，必须在模块层可见
language = "zh_CN"
locale_dirs = ["../locales/"]
gettext_compact = False


def setup(app):
    """注册 mystx 文档指令与并行读守卫，并声明本扩展并行安全。"""
    _register_docs_directives(app)
    _connect_parallel_guard(app)
    return {
        "version": release,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }

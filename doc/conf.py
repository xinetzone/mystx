#!/usr/bin/env python3
"""Sphinx 文档配置入口。

本文件自己持有站点画像、站点身份与站点级装配参数（可选扩展、告警抑制），并
负责定位仓库根目录；机制与画像的合并由 ``mystx.presets.assemble_site_config``
一次完成。

Sphinx 的契约是「conf.py 的模块命名空间即配置」：``sphinx.config`` 先 ``exec``
本文件，再以该命名空间构造 ``Config``。只有少数键必须在那个时刻就位——
``extensions``（加载扩展）与 ``language`` / ``locale_dirs`` / ``gettext_compact``
（i18n 初始化）早于 ``config-inited``；``version`` / ``release`` 一并显式给出，
让侧栏与页脚元数据一眼可见。其余键在 ``setup`` 注册的 ``config-inited`` 监听器
里统一下发：该事件早于核心校验与各扩展的消费，因此读到的是最终值。
"""

import os
import sys
from pathlib import Path
from typing import Any

from mystx.fonts import first_installed_family as _first_installed_family
from mystx.presets import assemble_site_config as _assemble_site_config
from mystx.presets import configure_site_fonts as _configure_site_fonts
from mystx.presets.xinetzone import icon_links as _icon_links
from mystx.presets.xinetzone import intersphinx_mapping as _intersphinx_mapping
from mystx.utils import resolve_site_url as _resolve_site_url

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "doc"))

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

# 社交卡片参数；字体取包内默认的 CJK 回退链（见 mystx.fonts），只传本机已装族
_ogp_social_cards: dict[str, Any] = {
    "site_url": "mystx.readthedocs.io",
    "image": "_static/images/logo.jpg",
    "line_colors": "#4078c0",
}
if (_ogp_font := _first_installed_family()) is not None:
    _ogp_social_cards["font"] = _ogp_font

# 站点画像：本站的全部取值（主题选项、OGP、文档工具），机制另由 mystx_site 装配
_profile: dict[str, Any] = {
    "ogp_site_url": "https://mystx.readthedocs.io/zh-cn/latest/",
    "ogp_social_cards": _ogp_social_cards,
    "html_theme_options": {
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
    },
    "autoapi_dirs": [str(ROOT / "src")],
    "autoapi_root": "autoapi",
    "autoapi_generate_api_docs": True,
    "bibtex_bibfiles": ["refs.bib"],
    # 作者个人的 intersphinx 源表（含本地清单缓存偏好）
    "intersphinx_mapping": _intersphinx_mapping(),
    "extlinks": {
        "daobook": ("https://daobook.github.io/%s", "Daobook %s"),
        "xinetzone": ("https://xinetzone.github.io/%s", "xinetzone %s"),
    },
    "nitpicky": os.environ.get("SPHINX_NITPICK", "").lower() in {"1", "true", "yes"},
}

# 字体注册是副作用，显式调用；字体目录由站点给出
_configure_site_fonts(ROOT / "doc" / "_static" / "fonts")

# 统一入口：机制取值（扩展、sitemap、默认值下放）与本站画像合并后一次返回。
# 非 RTD 由 mystx 生成 sitemap；CI 须显式给 SITEMAP_URL_BASE（项目型 Pages 带 /mystx/ 前缀）。
# 这里用站点自己的严格判定：DEFAULT_CONDITIONAL 只看 GITHUB_ACTIONS 是否存在，
# 会放过「CI 未声明 SITEMAP_URL_BASE」的情形，把 localhost 写进线上 sitemap。
_values, _setup = _assemble_site_config(
    profile=_profile,
    site_url=_resolve_site_url(require_on_ci=True),
    optional_extensions=OPTIONAL_EXTENSIONS,
    nitpick_ignore=NITPICK_IGNORE,
    suppress_warnings=SUPPRESS_WARNINGS,
)

# 站点身份：只有这一个站点，直接写在门面上，不经画像
project = "mystx"
author = "xinetzone"
copyright = "2026, xinetzone"

# 品牌资源：与站点身份同层由门面持有，画像不再重复
html_title = "Sphinx mystx Theme"
html_logo = "_static/images/logo.jpg"
html_favicon = "_static/images/favicon.jpg"

# 站点构建参数：只对本站有意义，直接写在门面上，不经画像
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_static_path = ["_static"]  # 自定义静态文件（样式表、脚本、图片）的源目录
html_last_updated_fmt = "%Y-%m-%d, %H:%M:%S"

# 站点行为开关：源文件链接、版本切换清单、评论组件
html_copy_source = True
# 用相对路径读本地清单：绝对 URL 会让 pydata 在构建期发请求校验，CI 阻网恒失败
version_switcher_json_url = "_static/switcher.json"
comments_config = {
    "hypothesis": True,
    "utterances": {"repo": "xinetzone/mystx", "optional": "config"},
}

# 早读键：Sphinx 在 config-inited 之前就要用，必须在模块层可见。
# 常量直接声明（测试断言其与机制取值一致，漂移即失败）；动态项取自统一入口。
extensions = _values["extensions"]
language = "zh_CN"
locale_dirs = ["../locales/"]
gettext_compact = False
version = release = _values["release"]

# 由本文件显式给出同名取值的键；其余键在 config-inited 阶段统一下发
_EXPLICIT_KEYS = frozenset({"extensions", "language", "locale_dirs", "gettext_compact", "version", "release"})


def _apply_profile(app, config):
    """把最终取值中未显式给出的键写入 ``config``（config-inited 阶段，先于任何消费者）。"""
    for name, value in _values.items():
        if name not in _EXPLICIT_KEYS:
            setattr(config, name, value)


def setup(app):
    # 优先级 0 先于核心校验与各扩展的 config-inited 处理（500-900），
    # 让类型检查与路径校验看到最终取值。
    app.connect("config-inited", _apply_profile, priority=0)
    return _setup(app)

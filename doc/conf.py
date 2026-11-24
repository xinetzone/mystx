#!/usr/bin/env python3
"""Sphinx 文档配置入口。

本文件自己持有站点身份与站点级装配（可选扩展、sitemap、告警抑制），并负责定位
仓库根目录、把画像分两段交给 Sphinx；画像取值在 ``mystx.presets.mystx_docs``。

Sphinx 的契约是「conf.py 的模块命名空间即配置」：``sphinx.config`` 先 ``exec``
本文件，再以该命名空间构造 ``Config``。但只有少数键必须在那个时刻就位——
``extensions`` 用于加载扩展，``language`` / ``locale_dirs`` / ``gettext_compact``
用于初始化 i18n，都发生在 ``config-inited`` 之前；``version`` / ``release``
一并显式给出，让侧栏与页脚元数据一眼可见。

其余键在 ``setup`` 注册的 ``config-inited`` 监听器里统一下发：该事件晚于扩展
加载、早于构建器创建与源文件扫描，核心校验（优先级 790-800）与各扩展的处理
都在其后，因此读到的是最终值。
"""

import sys
from pathlib import Path

from mystx.presets.mystx_docs import build_config
from mystx.presets.mystx_site import build_config as _build_site_config
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

# 画像先落、站点机制后覆盖，与原先「两次 update」的优先级一致
_profile = build_config(root=ROOT)
# 非 RTD 由 mystx 生成 sitemap；CI 须显式给 SITEMAP_URL_BASE（项目型 Pages 带 /mystx/ 前缀）。
# 这里用站点自己的严格判定：DEFAULT_CONDITIONAL 只看 GITHUB_ACTIONS 是否存在，
# 会放过「CI 未声明 SITEMAP_URL_BASE」的情形，把 localhost 写进线上 sitemap。
_site_values, _setup = _build_site_config(
    site_url=_resolve_site_url(require_on_ci=True),
    optional_extensions=OPTIONAL_EXTENSIONS,
    nitpick_ignore=NITPICK_IGNORE,
    suppress_warnings=SUPPRESS_WARNINGS,
)
_profile.update(_site_values)

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

# 早读键：Sphinx 在 config-inited 之前就要用，必须在模块层可见
extensions = _profile["extensions"]
language = _profile["language"]
locale_dirs = _profile["locale_dirs"]
gettext_compact = _profile["gettext_compact"]
version = _profile["version"]
release = _profile["release"]

# 画像中由本文件显式给出同名取值的键；不在画像里的（如品牌与构建参数）无需列入
_EXPLICIT_KEYS = frozenset({"extensions", "language", "locale_dirs", "gettext_compact", "version", "release"})


def _apply_profile(app, config):
    """把画像中未显式给出的键写入 ``config``（config-inited 阶段，先于任何消费者）。"""
    for name, value in _profile.items():
        if name not in _EXPLICIT_KEYS:
            setattr(config, name, value)


def setup(app):
    # 优先级 0 先于核心校验与各扩展的 config-inited 处理（500-900），
    # 让类型检查与路径校验看到最终取值。
    app.connect("config-inited", _apply_profile, priority=0)
    return _setup(app)

#!/usr/bin/env python3
"""
Sphinx 文档配置文件

该文件包含了 mystx 文档的所有配置项，包括项目信息、国际化设置、扩展插件、主题配置等。
"""
import os
import sys
from pathlib import Path

from sphinx.application import Sphinx

# mystx 包同时是本项目的复用层：并行守卫、MyST 文档工具指令、可选字体增强
# 与版本解析统一从包内导入，避免同一能力在 conf.py 与包内各留一份实现。
# 此处不设 try-except 降级：本文件的 autoapi 源目录与末尾无条件追加的
# mystx.ext.github_readme_stats 都依赖包本身，未安装 mystx 时构建不可能完成，
# 早退报 ImportError 比维护一条走不到的降级分支更诚实。
from mystx.config import DEFAULT_SITE_CONFIG
from mystx.fonts import configure_optional_matplotlib_fonts
from mystx.myst_docs import register_docs_directives
from mystx.parallel import connect_parallel_guard
from mystx.utils import resolve_release


# 设置路径
def get_project_root() -> Path:
    """获取项目根目录路径。"""
    return Path(__file__).resolve().parents[1]

ROOT = get_project_root()
sys.path.insert(0, str(ROOT / 'doc'))

release = resolve_release("mystx", env_var="MYSTX_VERSION", fallback="0.0.0")

# ================================= 项目基本信息 =================================
project = "mystx"
author = "xinetzone"
# epub 是 .readthedocs.yml 声明的 formats 之一，而 Sphinx 的 epub3 builder 要求
# copyright 与 version 均非空，否则构建期报「配置项不能为空」。RTD 侧已开
# fail_on_warning，这会直接把该 format 判红（实测复现）。version 取 release
# 即可：本包无 X.Y 短版本约定，取空值则 epub 产物的版本号本身也不合法。
copyright = "2026, xinetzone"
version = release
# ================================= 国际化与本地化设置 ==============================
language = 'zh_CN'       # 文档语言（中文简体）
locale_dirs = ['../locales/']  # 翻译文件存放目录
gettext_compact = False  # 是否合并子目录的PO文件（False表示不合并）

# ================================= 扩展插件配置 =================================
# conf.py 需先完成 sys.path 引导与项目元信息配置，此导入有意置于其后
import importlib.util as _ilut  # noqa: E402


def _has(mod: str) -> bool:
    return _ilut.find_spec(mod) is not None
extensions = [e for e in ['mystx'] if _has(e)]

# ================================= 可选：matplotlib 字体配置 =================================
# 字体增强的「包不可用 / 目录缺失 / 调用失败」三重守卫由包内
# configure_optional_matplotlib_fonts 统一实现：任一不满足只记日志、不阻断。
# ・RTD 仅安装 .[doc]（见 .readthedocs.yml），其依赖清单不含 taolib；
# ・浏览器端代码字体由 _static/font.css 的 @font-face 独立提供，与本块无关。
configure_optional_matplotlib_fonts(
    ROOT / 'doc/_static/fonts',
    families=('Maple Mono NF CN', 'Noto Color Emoji'),
)

# ================================= 文档构建配置 =================================
# 排除文件和目录模式
# README.md 面向仓库读者（徽章 / 安装命令 / 特性列表），不参与站点构建；
# 文档站的根入口见 index.md，仓库 README 通过「相关入口」链接引用。
exclude_patterns = [
    "_build",      # 构建输出目录
    "Thumbs.db",   # 缩略图数据库
    ".DS_Store",    # macOS 系统文件
    "README.md",   # 仓库 README 不纳入文档树
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
# 用**相对路径**指向本仓库的清单文件，不要写 http(s) 绝对 URL：
# pydata 对绝对 URL 会在构建期发 requests.get 校验，读不到即 warning；而本仓库
# CI 用 harden-runner 阻断出网（白名单不含 readthedocs.io），那道校验在 CI 上
# 必然失败——既产生噪声，又让这道校验永远走不到「通过」分支（守卫空转）；
# 且首次部署前该文件还不存在，绝对 URL 必然形成自举死锁。
# 相对路径改为读本地文件，校验照旧生效，前端按站点根解析，两条通道都取得到。
version_switcher_json_url = "_static/switcher.json"
# ================================= 可选插件 =================================
for _mod in [
    "sphinx_design",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx_comments",
    "mystx.ext.gallery",  # gallery-grid 指令（原 doc/_ext 副本已迁入包内）
]:
    if _has(_mod):
        extensions.append(_mod)
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

sitemap_locales = DEFAULT_SITE_CONFIG["sitemap_locales"]  # 语言列表

# 3. 参考文献配置
extensions.append('sphinxcontrib.bibtex')
bibtex_bibfiles = ['refs.bib']  # BibTeX 文件路径

# 4. API 文档自动生成
extensions.append("autoapi.extension")
autoapi_dirs = [str(ROOT/"src")]  # 源代码目录
autoapi_root = "autoapi"  # API 文档输出目录
autoapi_generate_api_docs = True  # 启用 API 文档生成

# 5. 图表生成配置
# 取值来自包内 DEFAULT_SITE_CONFIG（与项目身份无关的文档站通用键）
extensions.append("sphinx.ext.graphviz")
graphviz_output_format = DEFAULT_SITE_CONFIG["graphviz_output_format"]
inheritance_graph_attrs = DEFAULT_SITE_CONFIG["inheritance_graph_attrs"]

# 6. GitHub 贡献者显示
extensions.append('sphinx_contributors')

# 8. 社交媒体预览元数据
extensions.append("sphinxext.opengraph")
ogp_site_url = f"https://{project}.readthedocs.io/zh-cn/latest/"
ogp_social_cards = {
    "site_url": f"{project}.readthedocs.io",
    "image": "_static/images/logo.jpg",
    "font": "Maple Mono NF CN, SimHei, Microsoft YaHei",  # 支持中文字体，添加备选字体
    "line_colors": "#4078c0",
}

# 10. 丰富的悬停提示
extensions.append("sphinx_tippy")
tippy_rtd_urls = DEFAULT_SITE_CONFIG["tippy_rtd_urls"]

# =============================================================================
# 高级配置
# =============================================================================
# 忽略特定的 Nitpick 警告
# 前三条为上游实现导致的通用噪声，来自包内 DEFAULT_SITE_CONFIG；invoke 属
# 本项目可选依赖（未配置 intersphinx 清单），单独追加，仅豁免具体符号。
nitpick_ignore = [
    *DEFAULT_SITE_CONFIG["nitpick_ignore"],
    ("py:class", "invoke.Collection"),
]

# 抑制特定警告
suppress_warnings = [
    "mystnb.unknown_mime_type", "mystnb.mime_priority",
    "myst.xref_missing", "myst.domains",
    "ref.ref",
    "autoapi.python_import_resolution", "autoapi.not_readable",
    # epub builder 会扫描源目录，把 mimetypes 认不出的文件逐条告警；而
    # _static/switcher.json 是 pydata 前端要按站点根取用的切换清单，必须留在
    # _static（挪到别处前端就 404）。mimetypes 天然不认 .json，属误报，故抑制。
    "epub.unknown_project_files",
    "docutils",
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

extensions.extend([
    "sphinx.ext.intersphinx",  # 跨文档链接
    "sphinx.ext.extlinks",  # 短链接支持
    "sphinx_examples",  # 示例功能
])
# 交叉引用配置
intersphinx_mapping = {
    "python": ("https://docs.python.org/3.14", None),
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
    # MyST 文档工具指令（myst-config / myst-example 等）由包内统一注册：
    # 示例指令的 CSS 类名沿用 local.css 依赖的 myst-example* 契约。
    register_docs_directives(app)

    # P1-A 审计结论：新增第三方扩展时，如果其上游 setup() 未显式声明
    # parallel_{read,write}_safe=True，Sphinx 会将其视为 None 并退化为串行。
    # 覆写表与 fail-fast 守卫的实现见 mystx.parallel：表内补充扩展名即可
    # 启用并行，不再需要逐个去上游提 PR；守卫仅在显式要求并行时生效。
    # 审计参考: docs/retrospective/reports/documentation-governance/
    #           sphinx-parallel-build-5k-scale-20260903/index.md
    _PARALLEL_SAFE_OVERRIDES: dict[str, tuple[bool, bool]] = {
        # "autoapi.extension": (True, True),      # 需要时取消注释
        # "mystx.ext.gallery": (True, True),      # 需要时取消注释
    }
    connect_parallel_guard(app, _PARALLEL_SAFE_OVERRIDES)

    return {
        "version": release,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


nitpicky = os.environ.get("SPHINX_NITPICK", "").lower() in {"1", "true", "yes"}
templates_path = ["_templates"]

#!/usr/bin/env python3
"""
Sphinx 文档配置文件

该文件包含了 mystx 文档的所有配置项，包括项目信息、国际化设置、扩展插件、主题配置等。
"""
import os
import sys
from pathlib import Path

from sphinx.application import Sphinx


# 设置路径
def get_project_root() -> Path:
    """获取项目根目录路径。"""
    return Path(__file__).resolve().parents[1]

ROOT = get_project_root()
sys.path.insert(0, str(ROOT / 'doc'))
try:
    from importlib.metadata import version as _pkg_version
    release = _pkg_version("mystx")
except Exception:
    release = os.environ.get("MYSTX_VERSION", "0.0.0")
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
# taolib 与 doc/_static/fonts 均为可选增强，二者缺一即静默跳过：
# ・RTD 仅安装 .[doc]（见 .readthedocs.yml），其依赖清单不含 taolib；
# ・浏览器端代码字体由 _static/font.css 的 @font-face 独立提供，与本块无关。
# 守卫通过后仍失败时只提示、不阻断——该配置仅影响构建期 matplotlib 绘图的字形。
_font_directory = ROOT / 'doc/_static/fonts'
if _has('taolib') and _font_directory.is_dir():
    try:
        from taolib.fonts import configure_matplotlib_fonts
        configure_matplotlib_fonts(
            font_directory=_font_directory,
            families=('Maple Mono NF CN', 'Noto Color Emoji'),
        )
    except Exception as exc:
        print(f"[mystx] matplotlib 字体配置未生效，已跳过：{exc}")

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
    "_ext.gallery_directive",
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
    "font": "Maple Mono NF CN, SimHei, Microsoft YaHei",  # 支持中文字体，添加备选字体
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
    # autoapi 把类型注解中的 ``...`` 渲染成 ``Ellipsis`` 并按 py:class 交叉引用解析，
    # 但 Ellipsis 是内置单例、不在 intersphinx 清单中，无法解析；注解写法
    # （均为 tuple[X, ...]）不应为文档构建而改动，故仅精确豁免该符号。
    ("py:class", "Ellipsis"),
    # invoke 为可选第三方依赖，未配置 intersphinx 清单，故 invoke.Collection 无法解析；
    # 仅豁免这一个具体符号，不使用通配符压制整类 py:class 告警。
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
    from myst_parser._docs import (
        DirectiveDoc,
        DocutilsCliHelpDirective,
        MystAdmonitionDirective,
        MystConfigDirective,
        MystLexer,
        MystToHTMLDirective,
        MystWarningsDirective,
        NumberSections,
        StripUnsupportedLatex,
        SyntaxExampleDocsDirective,
    )

    # 项目仅支持 myst-parser >= 5.1（见 pyproject.toml 版本下界）：薄子类化仅
    # 把三个 CSS 类名钉回本仓 local.css 依赖的 myst-example* 契约；渲染语义
    # （源码/渲染双栏、无标题、sphinx-design div）沿用上游，注册名 "myst-example"
    # 与 doc/ 下既有用法保持不变。
    class MystExampleDirective(SyntaxExampleDocsDirective):
        wrapper_classes = ("myst-example",)
        source_classes = ("myst-example-source",)
        render_classes = ("myst-example-render",)

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

    # P1-A 审计结论：新增第三方扩展时，如果其上游 setup() 未显式声明
    # parallel_{read,write}_safe=True，Sphinx 会将其视为 None 并退化为串行。
    # 此处提供中心化覆写表，只需补充 extension_name 即可启用并行，
    # 不再需要逐个去上游提 PR。
    # 审计参考: docs/retrospective/reports/documentation-governance/
    #           sphinx-parallel-build-5k-scale-20260903/index.md
    _PARALLEL_SAFE_OVERRIDES: dict[str, tuple[bool, bool]] = {
        # "autoapi.extension":   (True, True),   # 需要时取消注释
        # "_ext.gallery_directive": (True, True),  # 需要时取消注释
    }
    for ext_name, (pr, pw) in _PARALLEL_SAFE_OVERRIDES.items():
        if ext_name in app.extensions:
            setattr(app.extensions[ext_name], "parallel_read_safe", bool(pr))
            setattr(app.extensions[ext_name], "parallel_write_safe", bool(pw))

    def _assert_parallel_ready(app, env, docnames):
        """Fail fast if any extension silently disabled parallel read.

        Gate: only fire when the caller actually requested parallelism
        via -j / $SPHINX_BUILD_JOBS so pure serial builds are not bothered.

        ``env-before-read-docs`` 事件契约为 (app, env, docnames) 三参，
        docnames 本钩子不使用但必须在签名中接收。
        """
        if app.parallel > 0 and not app.is_parallel_allowed("read"):
            raise RuntimeError(
                "Parallel read disabled. Check extensions missing "
                "parallel_read_safe=True. Re-run with -v to see per-extension "
                "warnings from Sphinx.is_parallel_allowed()."
            )

    app.connect("env-before-read-docs", _assert_parallel_ready)

    return {
        "version": release,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
nitpicky = os.environ.get("SPHINX_NITPICK", "").lower() in {"1", "true", "yes"}
templates_path = ["_templates"]

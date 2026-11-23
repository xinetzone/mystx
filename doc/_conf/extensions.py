"""扩展清单装配与各扩展的配置。

装配顺序即 ``extensions`` 列表的最终顺序，改动前先确认扩展间依赖
（例如 ``myst_parser`` 与 ``myst_nb`` 互斥，见 tests/unit/test_doc_parallel_extensions_p1.py）。
"""
import os

from mystx.config import DEFAULT_SITE_CONFIG

from .common import ROOT, has_module
from .meta import project

extensions = [e for e in ["mystx"] if has_module(e)]

# ================================= 可选插件 =================================
for _mod in [
    "sphinx_design",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx_comments",
    "mystx.ext.gallery",  # gallery-grid 指令（原 doc/_ext 副本已迁入包内）
]:
    if has_module(_mod):
        extensions.append(_mod)

# ================================= 可选功能配置 =================================
# 1. 代码复制按钮配置
copybutton_exclude = ".linenos, .gp"  # 排除行号和提示符
# 选择器配置，避免复制按钮出现在笔记本单元格编号上
copybutton_selector = ":not(.prompt) > div.highlight pre"
# 2. 评论系统配置
comments_config = {
    "hypothesis": True,  # 启用 Hypothesis 注释
    "utterances": {
        "repo": "xinetzone/mystx",
        "optional": "config",
    },  # 启用 Utterances 评论
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
extensions.append("sphinxcontrib.bibtex")
bibtex_bibfiles = ["refs.bib"]  # BibTeX 文件路径

# 4. API 文档自动生成
extensions.append("autoapi.extension")
autoapi_dirs = [str(ROOT / "src")]  # 源代码目录
autoapi_root = "autoapi"  # API 文档输出目录
autoapi_generate_api_docs = True  # 启用 API 文档生成

# 5. 图表生成配置
# 取值来自包内 DEFAULT_SITE_CONFIG（与项目身份无关的文档站通用键）
extensions.append("sphinx.ext.graphviz")
graphviz_output_format = DEFAULT_SITE_CONFIG["graphviz_output_format"]
inheritance_graph_attrs = DEFAULT_SITE_CONFIG["inheritance_graph_attrs"]

# 6. GitHub 贡献者显示
extensions.append("sphinx_contributors")

# 7. 社交媒体预览元数据
extensions.append("sphinxext.opengraph")
ogp_site_url = f"https://{project}.readthedocs.io/zh-cn/latest/"
ogp_social_cards = {
    "site_url": f"{project}.readthedocs.io",
    "image": "_static/images/logo.jpg",
    "font": "Maple Mono NF CN, SimHei, Microsoft YaHei",  # 支持中文字体，添加备选字体
    "line_colors": "#4078c0",
}

# 8. 丰富的悬停提示
extensions.append("sphinx_tippy")
tippy_rtd_urls = DEFAULT_SITE_CONFIG["tippy_rtd_urls"]

# 9. 跨文档链接与短链接（映射表见 myst 分组）
extensions.extend([
    "sphinx.ext.intersphinx",  # 跨文档链接
    "sphinx.ext.extlinks",  # 短链接支持
    "sphinx_examples",  # 示例功能
])

# 10. PyScript 插件
extensions.append("sphinx_pyscript")

# 11. GitHub 统计卡片插件
extensions.append("mystx.ext.github_readme_stats")

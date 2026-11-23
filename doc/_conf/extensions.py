"""扩展清单装配与各扩展配置（装配顺序即 ``extensions`` 的最终顺序）。"""
from mystx.config import DEFAULT_EXT_CONFIG, DEFAULT_SITE_CONFIG
from mystx.utils import resolve_site_url

from .common import ROOT, has_module
from .meta import project

extensions = [e for e in ["mystx"] if has_module(e)]

# 可选插件：未安装则跳过
for _mod in [
    "sphinx_design",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx_comments",
    "mystx.ext.gallery",
]:
    if has_module(_mod):
        extensions.append(_mod)

copybutton_exclude = DEFAULT_EXT_CONFIG["copybutton_exclude"]
copybutton_selector = DEFAULT_EXT_CONFIG["copybutton_selector"]
comments_config = {
    "hypothesis": True,
    "utterances": {"repo": "xinetzone/mystx", "optional": "config"},
}

# 非 RTD 由 mystx 生成 sitemap；CI 须显式给 SITEMAP_URL_BASE（项目型 Pages 带 /mystx/ 前缀）
site_url = resolve_site_url(require_on_ci=True)
html_baseurl = ""  # RTD 侧保持 Sphinx 默认值
if site_url:
    extensions.append("sphinx_sitemap")
    html_baseurl = site_url
    sitemap_url_scheme = "{link}"
else:
    sitemap_url_scheme = "{lang}{version}{link}"
sitemap_locales = DEFAULT_SITE_CONFIG["sitemap_locales"]

extensions.append("sphinxcontrib.bibtex")
bibtex_bibfiles = ["refs.bib"]

extensions.append("autoapi.extension")
autoapi_dirs = [str(ROOT / "src")]
autoapi_root = "autoapi"
autoapi_generate_api_docs = True

extensions.append("sphinx.ext.graphviz")
graphviz_output_format = DEFAULT_SITE_CONFIG["graphviz_output_format"]
inheritance_graph_attrs = DEFAULT_SITE_CONFIG["inheritance_graph_attrs"]

extensions.append("sphinx_contributors")

extensions.append("sphinxext.opengraph")
ogp_site_url = f"https://{project}.readthedocs.io/zh-cn/latest/"
ogp_social_cards = {
    "site_url": f"{project}.readthedocs.io",
    "image": "_static/images/logo.jpg",
    "font": "Maple Mono NF CN, SimHei, Microsoft YaHei",
    "line_colors": "#4078c0",
}

extensions.append("sphinx_tippy")
tippy_rtd_urls = DEFAULT_SITE_CONFIG["tippy_rtd_urls"]

extensions.extend(["sphinx.ext.intersphinx", "sphinx.ext.extlinks", "sphinx_examples"])
extensions.append("sphinx_pyscript")
extensions.append("mystx.ext.github_readme_stats")

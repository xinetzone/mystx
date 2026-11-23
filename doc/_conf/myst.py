"""MyST 解析、交叉引用、短链接与告警抑制配置。"""
import os

from mystx.config import DEFAULT_BUILD_CONFIG, DEFAULT_MYST_CONFIG, DEFAULT_SITE_CONFIG

# 前三条为上游通用噪声（来自 DEFAULT_SITE_CONFIG）；invoke 为本项目可选依赖
nitpick_ignore = [
    *DEFAULT_SITE_CONFIG["nitpick_ignore"],
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
    "epub.unknown_project_files",  # epub 扫描 _static/switcher.json 的误报
    "docutils",
]

numfig = DEFAULT_BUILD_CONFIG["numfig"]
# 复制一份，避免站点侧改动污染包内默认值
myst_enable_extensions = list(DEFAULT_MYST_CONFIG["myst_enable_extensions"])

intersphinx_mapping = {
    "python": ("https://docs.python.org/3.14", None),
    "sphinx": ("https://daobook.github.io/sphinx/", None),
    "pst": ("https://daobook.github.io/pydata-sphinx-theme/", None),
    "sbt": ("https://daobook.github.io/sphinx-book-theme/", None),
    "myst-nb": ("https://daobook.github.io/MyST-NB/", None),
    "myst-parser": ("https://daobook.github.io/MyST-Parser/", None),
}

extlinks = {
    "daobook": ("https://daobook.github.io/%s", "Daobook %s"),
    "xinetzone": ("https://xinetzone.github.io/%s", "xinetzone %s"),
}

nitpicky = os.environ.get("SPHINX_NITPICK", "").lower() in {"1", "true", "yes"}

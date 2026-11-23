"""MyST 解析、交叉引用、短链接与告警抑制配置。"""
import os

from mystx.config import DEFAULT_SITE_CONFIG

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
    "daobook": ("https://daobook.github.io/%s", "Daobook %s"),
    "xinetzone": ("https://xinetzone.github.io/%s", "xinetzone %s"),
}

nitpicky = os.environ.get("SPHINX_NITPICK", "").lower() in {"1", "true", "yes"}

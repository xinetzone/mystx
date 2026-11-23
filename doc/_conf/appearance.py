"""主题、静态资源、字体增强与站点前端配置。"""
from mystx.fonts import configure_optional_matplotlib_fonts
from mystx.themes import resolve_theme

from .common import ROOT

# README.md 面向仓库读者，站点根入口为 index.md
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "README.md"]

html_static_path = ["_static"]
html_css_files = ["local.css", "font.css"]
html_last_updated_fmt = "%Y-%m-%d, %H:%M:%S"
templates_path = ["_templates"]

# 回退链（mystx → sphinx_book_theme → alabaster）由包内 themes 唯一维护
html_theme = resolve_theme()
html_title = "Sphinx mystx Theme"
html_logo = "_static/images/logo.jpg"
html_favicon = "_static/images/favicon.jpg"
html_copy_source = True

# 字体增强的三重守卫（包不可用 / 目录缺失 / 调用失败）由包内实现，仅记日志
configure_optional_matplotlib_fonts(
    ROOT / "doc/_static/fonts",
    families=("Maple Mono NF CN", "Noto Color Emoji"),
)

# 用相对路径读本地清单：绝对 URL 会让 pydata 构建期发请求校验，CI 阻网恒失败
version_switcher_json_url = "_static/switcher.json"

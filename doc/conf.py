"""mystx 文档站配置（P0/P1 最小站点）。"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

project = "mystx"
author = "xinetzone"
copyright = "2026, xinetzone"

extensions = ["mystx"]

html_theme = "mystx"
html_title = "mystx"
html_static_path = []
exclude_patterns = ["_build"]

# 站点只覆盖需要显式表达的值；其余取 theme.toml 默认。
html_theme_options = {
    "book_nav_scope": "book",
    "book_nav_depth": 3,
}

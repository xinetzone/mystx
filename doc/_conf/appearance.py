"""主题决策与字体增强（纯取值已迁至 ``doc/_config.toml``）。"""
from mystx.fonts import configure_optional_matplotlib_fonts
from mystx.themes import resolve_theme

from .common import ROOT

# 回退链（mystx → sphinx_book_theme → alabaster）由包内 themes 唯一维护
html_theme = resolve_theme()

# 字体增强的三重守卫（包不可用 / 目录缺失 / 调用失败）由包内实现，仅记日志
configure_optional_matplotlib_fonts(
    ROOT / "doc/_static/fonts",
    families=("Maple Mono NF CN", "Noto Color Emoji"),
)

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Sequence

from sphinx.application import Sphinx
from sphinx.util import logging as sphinx_logging

from .utils import deep_merge, has_module

DEFAULT_THEME_PRIORITY: tuple[str, ...] = (
    "mystx",
    "sphinx_book_theme",
    "alabaster",
)


def resolve_theme(
    priority: Sequence[str] = DEFAULT_THEME_PRIORITY,
    *,
    extra_before: Sequence[str] = (),
    extra_after: Sequence[str] = (),
) -> str:
    """按优先级队列选择第一个已安装的主题（公理 A4 实现）。

    默认回退链：``mystx → sphinx_book_theme → alabaster``；
    其中 ``alabaster`` 是 Sphinx 内置主题，保证永不缺失。

    参数 ``extra_before`` / ``extra_after`` 允许在默认队列前后插入自定义主题：
    ``extra_before`` 的项目**优先于**默认主题；``extra_after`` 的项目排在默认
    主题之后、**alabaster 之前**——保证回退到 alabaster 始终是最后一条。
    """
    full: list[str] = []
    full.extend(extra_before)
    for t in priority:
        if t == "alabaster":
            continue
        full.append(t)
    full.extend(extra_after)
    full.append("alabaster")
    for theme in full:
        if theme == "alabaster":
            return "alabaster"
        if has_module(theme):
            return theme
    return "alabaster"


DEFAULT_BOOK_THEME_OPTIONS: dict[str, object] = {
    "use_repository_button": True,
    "repository_branch": "main",
    "use_source_button": True,
    "use_edit_page_button": False,
    "use_issues_button": True,
    "path_to_docs": "doc",
    "toc_title": "目录",
    "show_navbar_depth": 10,
    "max_navbar_depth": 4,
    "collapse_navbar": False,
    "use_download_button": True,
    "use_fullscreen_button": True,
    "footer_content_items": "author.html, copyright.html, last-updated.html, extra-footer.html",
    "navbar_persistent": [],
}


def resolve_theme_options(
    theme: str,
    override: dict[str, object] | None = None,
    *,
    book_defaults: dict[str, object] = DEFAULT_BOOK_THEME_OPTIONS,
) -> dict[str, object]:
    """根据选定主题合并默认 theme_options。

    目前对 ``sphinx_book_theme`` / ``mystx`` 提供完整默认字典；
    其他主题返回空字典或 override 原样。
    """
    base: dict[str, object] = {}
    if theme in ("sphinx_book_theme", "mystx"):
        base = dict(book_defaults)
    return deep_merge(base, override or {})


# ---------------------------------------------------------------------------
# 主题注册器：将 mystx/theme/<name> 目录注册为 Sphinx HTML 主题
# ---------------------------------------------------------------------------

_theme_logger = sphinx_logging.getLogger(__name__)


@dataclass(slots=True)
class MySTX:
    """mystx 主题注册器：定位主题目录并调用 app.add_html_theme()。

    Attributes:
        app: Sphinx 应用实例，用于注册主题。
        name: 主题名称，默认为 ``"mystx"``，对应 ``theme/<name>/`` 子目录。
        theme_dir: 解析后的主题目录绝对路径，``__post_init__`` 中自动设置。
    """

    app: Sphinx
    name: str = "mystx"
    theme_dir: Optional[str] = field(init=False)

    def __post_init__(self) -> None:
        parent = Path(__file__).parent.resolve()
        theme_dir = parent / "theme" / self.name
        if not theme_dir.exists():
            _theme_logger.error(f"主题目录未找到: {theme_dir}")
            raise FileNotFoundError(f"主题目录未找到: {theme_dir}")
        self.theme_dir = str(theme_dir)
        try:
            self.app.add_html_theme(self.name, self.theme_dir)
        except Exception as e:
            _theme_logger.error(f"注册 {self.name} 主题时发生错误: {e}", exc_info=True)
            raise
        _theme_logger.info(f"{self.name} 主题已成功注册")

"""主题选择、主题选项默认值与 mystx 主题注册。

主题优先级与书系主题名单是本模块的单一权威源：运行期结构性默认、站点配置与
``doc/_conf`` 均从这里取值，包内不再维护第二份名单。
"""
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

from sphinx.application import Sphinx

from .utils import deep_merge, has_module

#: 书系主题名单的唯一权威源（主题选择、选项注入、运行期默认均引用此常量）。
BOOK_THEME_NAMES: tuple[str, ...] = (
    "mystx",
    "sphinx_book_theme",
)

DEFAULT_THEME_PRIORITY: tuple[str, ...] = (
    *BOOK_THEME_NAMES,
    "alabaster",
)


def resolve_theme(
    priority: Sequence[str] = DEFAULT_THEME_PRIORITY,
    *,
    extra_before: Sequence[str] = (),
    extra_after: Sequence[str] = (),
) -> str:
    """按优先级队列选择第一个已安装的主题。

    默认回退链为 ``mystx → sphinx_book_theme → alabaster``。``alabaster`` 是
    Sphinx 内置主题，作为**无条件兜底**始终排在最后，故队列中的同名项会被忽略。

    Args:
        priority: 默认优先级队列，按序取第一个可导入的主题。
        extra_before: 插在默认队列之前，优先于默认主题。
        extra_after: 插在默认队列之后、兜底之前。
    """
    candidates = (
        *extra_before,
        *(theme for theme in priority if theme != "alabaster"),
        *extra_after,
    )
    return next((theme for theme in candidates if has_module(theme)), "alabaster")


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
    """按选定主题合并默认 ``html_theme_options``：书系主题取完整默认值，其余为空字典。"""
    base = dict(book_defaults) if theme in BOOK_THEME_NAMES else {}
    return deep_merge(base, override or {})


@dataclass(slots=True)
class MySTX:
    """把 ``theme/<name>/`` 目录注册为 Sphinx HTML 主题。

    Attributes:
        app: Sphinx 应用实例。
        name: 主题名，默认 ``"mystx"``，对应 ``theme/<name>/`` 子目录。
        theme_dir: 解析后的主题目录绝对路径，``__post_init__`` 中设置。
    """

    app: Sphinx
    name: str = "mystx"
    theme_dir: str | None = field(init=False)

    def __post_init__(self) -> None:
        theme_dir = Path(__file__).parent.resolve() / "theme" / self.name
        if not theme_dir.is_dir():
            raise FileNotFoundError(f"主题目录未找到: {theme_dir}")
        self.theme_dir = str(theme_dir)
        self.app.add_html_theme(self.name, self.theme_dir)

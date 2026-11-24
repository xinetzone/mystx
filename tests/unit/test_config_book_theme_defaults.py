"""书系主题 ``html_theme_options`` 默认值注入逻辑的单元测试。

背景一：pydata-sphinx-theme 在 builder-inited 阶段会给未声明
``navbar_persistent`` 的项目自动注入顶栏搜索按钮，与书系主题主侧边栏
内置的搜索按钮叠加成双搜索框。mystx 在 config-inited 阶段以
setdefault 语义补齐空列表，本测试守护该契约。

背景二：``mystx`` 主题的 Python 侧消费者只读 ``config.html_theme_options``，
不读 ``theme.toml``；因此 mystx 站点由扩展补全完整主题默认值，conf.py
只声明覆盖项。第三方 ``sphinx_book_theme`` 站点不享受这些默认值。
"""

from types import SimpleNamespace

from mystx.config import apply_book_theme_option_defaults
from mystx.themes import DEFAULT_BOOK_THEME_OPTIONS


def _make_config(theme: str, options: dict | None = None):
    return SimpleNamespace(html_theme=theme, html_theme_options=options if options is not None else {})


def test_mystx_theme_missing_key_gets_empty_list():
    config = _make_config("mystx")
    apply_book_theme_option_defaults(config)
    assert config.html_theme_options["navbar_persistent"] == []


def test_mystx_theme_gets_full_defaults():
    config = _make_config("mystx", {"announcement": "hello"})
    apply_book_theme_option_defaults(config)
    for key, value in DEFAULT_BOOK_THEME_OPTIONS.items():
        assert config.html_theme_options[key] == value, key
    assert config.html_theme_options["announcement"] == "hello"


def test_mystx_theme_explicit_value_wins_over_defaults():
    config = _make_config("mystx", {"use_repository_button": False, "use_sidenotes": False})
    apply_book_theme_option_defaults(config)
    assert config.html_theme_options["use_repository_button"] is False
    assert config.html_theme_options["use_sidenotes"] is False


def test_sphinx_book_theme_only_gets_navbar_default():
    """第三方书系站点只补 navbar_persistent，不接管 mystx 的其余默认值。"""
    config = _make_config("sphinx_book_theme")
    apply_book_theme_option_defaults(config)
    assert config.html_theme_options["navbar_persistent"] == []
    for key in DEFAULT_BOOK_THEME_OPTIONS:
        if key == "navbar_persistent":
            continue
        assert key not in config.html_theme_options, key


def test_explicit_user_value_is_preserved():
    config = _make_config("mystx", {"navbar_persistent": ["search-button-field"]})
    apply_book_theme_option_defaults(config)
    assert config.html_theme_options["navbar_persistent"] == ["search-button-field"]


def test_explicit_empty_list_stays_empty():
    config = _make_config("mystx", {"navbar_persistent": []})
    apply_book_theme_option_defaults(config)
    assert config.html_theme_options["navbar_persistent"] == []


def test_other_themes_are_untouched():
    config = _make_config("alabaster")
    apply_book_theme_option_defaults(config)
    assert "navbar_persistent" not in config.html_theme_options


def test_book_theme_names_are_single_sourced_from_themes():
    """门面与运行期须直接引用 ``themes`` 的名单，不经 ``defaults`` 中转副本。"""
    import mystx.themes as themes
    from mystx import config
    from mystx.config import runtime

    assert config.BOOK_THEME_NAMES is themes.BOOK_THEME_NAMES
    assert runtime.BOOK_THEME_NAMES is themes.BOOK_THEME_NAMES

"""书系主题结构性默认选项（navbar_persistent）注入逻辑的单元测试。

背景：pydata-sphinx-theme 在 builder-inited 阶段会给未声明
``navbar_persistent`` 的项目自动注入顶栏搜索按钮，与书系主题主侧边栏
内置的搜索按钮叠加成双搜索框。mystx 在 config-inited 阶段以
setdefault 语义补齐空列表，本测试守护该契约。
"""
from types import SimpleNamespace

from mystx.config import apply_book_theme_option_defaults


def _make_config(theme: str, options: dict | None = None):
    return SimpleNamespace(html_theme=theme, html_theme_options=options if options is not None else {})


def test_mystx_theme_missing_key_gets_empty_list():
    config = _make_config("mystx")
    apply_book_theme_option_defaults(config)
    assert config.html_theme_options["navbar_persistent"] == []


def test_sphinx_book_theme_missing_key_gets_empty_list():
    config = _make_config("sphinx_book_theme")
    apply_book_theme_option_defaults(config)
    assert config.html_theme_options["navbar_persistent"] == []


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

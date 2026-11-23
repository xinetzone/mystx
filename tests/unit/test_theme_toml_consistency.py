"""theme.toml 与 ``themes.DEFAULT_BOOK_THEME_OPTIONS`` 的一致性守卫。

mystx 的默认值有两条生效路径：纯主题路径读 ``theme.toml``，preset 路径由
``html_theme_options`` 注入 Python 字典（后者优先）。两者必须给出同一默认值，
否则同一主题在不同接入方式下呈现不同行为。本测试把这条不变量固化为机检门禁。

``navbar_persistent`` 例外：theme.conf 只能存字符串，运行期由 config-inited
统一注入列表 ``[]``，故不参与比较。
"""

import tomllib
from pathlib import Path

import mystx
from mystx.themes import DEFAULT_BOOK_THEME_OPTIONS

THEME_TOML = Path(mystx.__file__).parent / "theme" / "mystx" / "theme.toml"

_EXEMPT = {"navbar_persistent"}


def test_theme_toml_matches_python_defaults():
    options = tomllib.loads(THEME_TOML.read_text(encoding="utf-8"))["options"]
    shared = {
        key: value
        for key, value in DEFAULT_BOOK_THEME_OPTIONS.items()
        if key in options and key not in _EXEMPT
    }
    assert shared, "theme.toml 与 Python 默认字典应至少共享一个键"

    mismatched = {
        key: (value, options[key])
        for key, value in shared.items()
        if str(value) != options[key]
    }
    assert not mismatched, f"theme.toml 与 Python 默认值分歧: {mismatched}"

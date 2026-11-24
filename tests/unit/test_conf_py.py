"""doc/conf.py 的萃取契约测试：确认它消费包内预设而非自留机制副本。

本文件只做「装配面」断言，不启动 Sphinx 构建：目标是把 conf.py 与
``mystx`` 包之间的复用关系固化为机检门禁，避免日后又长回一份内联实现。
"""

import importlib.util
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from mystx.config import (
    DEFAULT_BUILD_CONFIG,
    DEFAULT_EXT_CONFIG,
    DEFAULT_MYST_CONFIG,
)
from mystx.presets.mystx_docs import build_config
from mystx.presets.mystx_site import build_config as build_site_config
from mystx.themes import resolve_theme, resolve_theme_options
from mystx.utils import resolve_site_url

CONF_PATH = Path(__file__).resolve().parents[2] / "doc" / "conf.py"


def _load_conf():
    spec = importlib.util.spec_from_file_location("mystx_doc_conf", CONF_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _require_upstream_docs():
    """本机 myst-parser 低于 5.1 时跳过装配测试（pyproject 已声明下界）。"""
    docs = pytest.importorskip("myst_parser._docs")
    if not hasattr(docs, "SyntaxExampleDocsDirective"):
        pytest.skip("本机 myst-parser < 5.1，缺少 SyntaxExampleDocsDirective")


def _expected_profile(conf):
    """按 conf.py 的装配顺序重算期望取值：画像 + 站点机制 + 主题选项补全。"""
    profile = {**build_config(root=CONF_PATH.parents[1])}
    site_values, _ = build_site_config(
        site_url=resolve_site_url(require_on_ci=True),
        optional_extensions=conf.OPTIONAL_EXTENSIONS,
        nitpick_ignore=conf.NITPICK_IGNORE,
        suppress_warnings=conf.SUPPRESS_WARNINGS,
    )
    profile.update(site_values)
    profile["html_theme_options"] = resolve_theme_options(
        profile["html_theme"], profile["html_theme_options"]
    )
    return profile


def test_conf_owns_identity_and_exposes_early_keys():
    """身份字段由 conf.py 直接持有；早读键取自画像；其余键由监听器整体下发。"""
    conf = _load_conf()
    expected = _expected_profile(conf)

    assert conf.build_config is build_config
    assert callable(conf.setup)
    assert (conf.project, conf.author, conf.copyright) == ("mystx", "xinetzone", "2026, xinetzone")
    assert not {"project", "author", "copyright"} & set(expected)
    # 早读键必须在模块命名空间里，取值与画像一致
    for name in conf._EXPLICIT_KEYS:
        assert getattr(conf, name) == expected[name], name

    config = SimpleNamespace()
    conf._apply_profile(None, config)
    applied = vars(config)
    assert set(applied) == set(expected) - set(conf._EXPLICIT_KEYS)
    for name, value in applied.items():
        assert value == expected[name], name
    # 延迟下发的键不在模块层留第二份，避免两处取值漂移
    assert not set(applied) & set(vars(conf))
    assert "mystx.ext.gallery" in conf.extensions
    assert ("py:class", "invoke.Collection") in applied["nitpick_ignore"]


def test_conf_keeps_no_inline_mechanism_copies():
    """机制已迁入预设：conf.py 命名空间不再暴露实现符号，取值仍与包内同源。"""
    conf = _load_conf()
    config = SimpleNamespace()
    conf._apply_profile(None, config)

    for name in (
        "register_docs_directives",
        "connect_parallel_guard",
        "resolve_extensions",
        "apply_site_config",
        "configure_site_fonts",
    ):
        assert not hasattr(conf, name)
    # 装配是单次调用，命名空间里不应残留中间变量或 update 痕迹
    assert not hasattr(conf, "conf")
    assert not hasattr(conf, "_site")
    assert config.html_theme == resolve_theme()
    assert config.numfig == DEFAULT_BUILD_CONFIG["numfig"]
    assert config.myst_enable_extensions == DEFAULT_MYST_CONFIG["myst_enable_extensions"]
    assert config.copybutton_exclude == DEFAULT_EXT_CONFIG["copybutton_exclude"]
    assert config.copybutton_selector == DEFAULT_EXT_CONFIG["copybutton_selector"]


def test_conf_setup_registers_config_inited_docs_directives_and_parallel_guard():
    _require_upstream_docs()
    conf = _load_conf()
    app = MagicMock()

    meta = conf.setup(app)

    registered = [call.args[0] for call in app.add_directive.call_args_list]
    assert "myst-config" in registered
    assert "myst-example" in registered
    events = [call.args[0] for call in app.connect.call_args_list]
    assert events == ["config-inited", "env-before-read-docs"]
    assert app.connect.call_args_list[0].kwargs["priority"] == 0
    # 注册到 Sphinx 的正是下发剩余画像的那个监听器
    config = SimpleNamespace()
    listener = app.connect.call_args_list[0].args[1]
    listener(app, config)
    expected = _expected_profile(conf)
    assert set(vars(config)) == set(expected) - set(conf._EXPLICIT_KEYS)
    assert meta["version"] == conf.release
    assert meta["parallel_read_safe"] is True

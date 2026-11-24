"""doc/conf.py 的萃取契约测试：确认它消费包内预设而非自留机制副本。

本文件只做「装配面」断言，不启动 Sphinx 构建：目标是把 conf.py 与
``mystx`` 包之间的复用关系固化为机检门禁，避免日后又长回一份内联实现。
"""
import importlib.util
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from mystx.config import (
    DEFAULT_BUILD_CONFIG,
    DEFAULT_EXT_CONFIG,
    DEFAULT_MYST_CONFIG,
    DEFAULT_SITE_CONFIG,
)
from mystx.presets.mystx_docs import build_config
from mystx.themes import resolve_theme

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


def test_conf_consumes_site_preset():
    conf = _load_conf()

    assert conf.build_config is build_config
    assert callable(conf.setup)
    # 画像每新增一个键，conf.py 必须显式赋值，否则此处失败
    expected, _ = build_config(root=CONF_PATH.parents[1])
    missing = set(expected) - set(vars(conf))
    assert not missing, f"conf.py 未显式赋值：{sorted(missing)}"
    assert conf.release and conf.version == conf.release
    assert "mystx.ext.gallery" in conf.extensions
    assert ("py:class", "invoke.Collection") in conf.nitpick_ignore
    assert conf.graphviz_output_format == DEFAULT_SITE_CONFIG["graphviz_output_format"]
    assert conf.tippy_rtd_urls == DEFAULT_SITE_CONFIG["tippy_rtd_urls"]


def test_conf_keeps_no_inline_mechanism_copies():
    """机制已迁入预设：conf.py 命名空间不再暴露实现符号，取值仍与包内同源。"""
    conf = _load_conf()

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
    assert conf.html_theme == resolve_theme()
    assert conf.numfig == DEFAULT_BUILD_CONFIG["numfig"]
    assert conf.myst_enable_extensions == DEFAULT_MYST_CONFIG["myst_enable_extensions"]
    assert conf.copybutton_exclude == DEFAULT_EXT_CONFIG["copybutton_exclude"]
    assert conf.copybutton_selector == DEFAULT_EXT_CONFIG["copybutton_selector"]


def test_conf_setup_registers_docs_directives_and_parallel_guard():
    _require_upstream_docs()
    conf = _load_conf()
    app = MagicMock()

    meta = conf.setup(app)

    registered = [call.args[0] for call in app.add_directive.call_args_list]
    assert "myst-config" in registered
    assert "myst-example" in registered
    app.connect.assert_called_once()
    assert meta["version"] == conf.release
    assert meta["parallel_read_safe"] is True

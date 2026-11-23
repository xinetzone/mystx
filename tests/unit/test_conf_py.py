"""doc/conf.py 的萃取契约测试：确认它消费包内模块而非自留副本。

本文件只做「装配面」断言，不启动 Sphinx 构建：目标是把 conf.py 与
``mystx`` 包之间的复用关系固化为机检门禁，避免日后又长回一份内联实现。
"""
import importlib.util
from pathlib import Path
from unittest.mock import MagicMock

import pytest

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


def test_conf_consumes_package_layer():
    conf = _load_conf()

    assert callable(conf.register_docs_directives)
    assert callable(conf.connect_parallel_guard)
    assert conf.release and conf.version == conf.release
    assert "mystx.ext.gallery" in conf.extensions
    assert ("py:class", "invoke.Collection") in conf.nitpick_ignore
    assert conf.graphviz_output_format == conf.DEFAULT_SITE_CONFIG["graphviz_output_format"]
    assert conf.tippy_rtd_urls == conf.DEFAULT_SITE_CONFIG["tippy_rtd_urls"]


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

"""mystx.myst_docs 的单元测试：类名派生、指令注册与可选开关。"""
from unittest.mock import MagicMock

import pytest

from mystx.myst_docs import (
    DEFAULT_EXAMPLE_PREFIX,
    DOCS_DIRECTIVE_NAMES,
    example_classes,
    make_example_directive,
    register_docs_directives,
)


class _FakeBase:
    """替代上游 SyntaxExampleDocsDirective 的最小基类。"""

    wrapper_classes = ("upstream",)
    source_classes = ("upstream-source",)
    render_classes = ("upstream-render",)


def test_example_classes_derives_three_names():
    assert example_classes() == ("myst-example", "myst-example-source", "myst-example-render")
    assert DEFAULT_EXAMPLE_PREFIX == "myst-example"
    assert example_classes("demo") == ("demo", "demo-source", "demo-render")


def test_make_example_directive_pins_classes_on_subclass():
    directive = make_example_directive(base=_FakeBase)

    assert issubclass(directive, _FakeBase)
    assert directive.wrapper_classes == ("myst-example",)
    assert directive.source_classes == ("myst-example-source",)
    assert directive.render_classes == ("myst-example-render",)


def test_make_example_directive_respects_prefix():
    directive = make_example_directive("custom", base=_FakeBase)

    assert directive.wrapper_classes == ("custom",)
    assert directive.source_classes == ("custom-source",)
    assert directive.render_classes == ("custom-render",)


def _fake_factory(prefix=DEFAULT_EXAMPLE_PREFIX, *, base=None):
    return _FakeBase


def _require_upstream_docs():
    """本机 myst-parser 低于 5.1 时跳过注册测试（pyproject 已声明下界）。"""
    docs = pytest.importorskip("myst_parser._docs")
    if not hasattr(docs, "SyntaxExampleDocsDirective"):
        pytest.skip("本机 myst-parser < 5.1，缺少 SyntaxExampleDocsDirective")


def test_register_docs_directives_registers_all_names(monkeypatch):
    _require_upstream_docs()
    import mystx.myst_docs as mod

    monkeypatch.setattr(mod, "make_example_directive", _fake_factory)
    app = MagicMock()

    register_docs_directives(app)

    registered = [c.args[0] for c in app.add_directive.call_args_list]
    assert tuple(registered) == DOCS_DIRECTIVE_NAMES
    assert app.add_post_transform.call_count == 2
    app.add_lexer.assert_called_once()


def test_register_docs_directives_can_skip_transforms_and_lexer(monkeypatch):
    _require_upstream_docs()
    import mystx.myst_docs as mod

    monkeypatch.setattr(mod, "make_example_directive", _fake_factory)
    app = MagicMock()

    register_docs_directives(app, register_transforms=False, register_lexer=False)

    app.add_post_transform.assert_not_called()
    app.add_lexer.assert_not_called()


def test_register_docs_directives_raises_informative_import_error(monkeypatch):
    import sys

    monkeypatch.setitem(sys.modules, "myst_parser._docs", None)

    with pytest.raises(ImportError, match="myst-parser"):
        register_docs_directives(MagicMock())

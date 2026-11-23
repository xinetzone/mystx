"""mystx.fonts 的单元测试：三重守卫与静默降级语义。"""
import importlib.machinery
import sys
import types

from mystx.fonts import configure_optional_matplotlib_fonts


def _install_fake(monkeypatch, name: str, configure) -> types.ModuleType:
    """注册一个有合法 ``__spec__`` 的假模块（import_module 需要）。"""
    fake = types.ModuleType(name)
    fake.__spec__ = importlib.machinery.ModuleSpec(name, None)
    fake.configure_matplotlib_fonts = configure
    monkeypatch.setitem(sys.modules, name, fake)
    return fake


def test_returns_false_when_module_missing(tmp_path):
    assert (
        configure_optional_matplotlib_fonts(tmp_path, ("Demo",), module="___no_such_font_module___")
        is False
    )


def test_returns_false_when_directory_missing(tmp_path):
    assert configure_optional_matplotlib_fonts(tmp_path / "absent", ("Demo",)) is False


def test_returns_true_and_forwards_arguments(tmp_path, monkeypatch):
    calls = {}

    def _configure(*, font_directory, families):
        calls["font_directory"] = font_directory
        calls["families"] = families

    _install_fake(monkeypatch, "fake_font_backend", _configure)

    ok = configure_optional_matplotlib_fonts(
        tmp_path, ["A", "B"], module="fake_font_backend"
    )

    assert ok is True
    assert calls["font_directory"] == tmp_path
    assert calls["families"] == ("A", "B")


def test_returns_false_when_backend_raises(tmp_path, monkeypatch):
    def _boom(**_kwargs):
        raise RuntimeError("no glyph")

    _install_fake(monkeypatch, "boom_font_backend", _boom)

    assert configure_optional_matplotlib_fonts(tmp_path, ("A",), module="boom_font_backend") is False

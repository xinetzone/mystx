import inspect
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from sphinx.application import Sphinx
from sphinx.config import Config


def test_entrypoint_imports():
    from mystx.themes import MySTX
    from mystx.config import ConfigManager, config_inited_handler
    from mystx.version_switcher import sphinx_setup as _vss
    from mystx import setup as _mystx_setup

    assert callable(_mystx_setup)


def test_setup_returns_parallel_safe_schema():
    from mystx import setup as _mystx_setup
    from mystx.themes import MySTX
    from mystx.config import ConfigManager
    from mystx.version_switcher import sphinx_setup as version_switcher_setup
    from mystx import _setup_myst_nb

    sig_cm = inspect.signature(ConfigManager)
    cm_params = list(sig_cm.parameters.keys())
    assert cm_params[:3] == ["app", "config", "logger"], f"ConfigManager params: {cm_params}"

    sig_mystx = inspect.signature(MySTX)
    mystx_params = list(sig_mystx.parameters.keys())
    assert "app" in mystx_params, f"MySTX params: {mystx_params}"

    sig_vss = inspect.signature(version_switcher_setup)
    vss_params = list(sig_vss.parameters.keys())
    assert vss_params == ["app", "config"], f"version_switcher_setup params: {vss_params}"

    sig_mnb = inspect.signature(_setup_myst_nb)
    mnb_params = list(sig_mnb.parameters.keys())
    assert mnb_params == ["app"], f"_setup_myst_nb params: {mnb_params}"

    class _MockExtensions(dict):
        pass

    class _Config:
        extensions = ["myst_parser"]
        html_theme_options = {}
        release = "0.1.0"

    m = MagicMock()
    m.config = _Config()
    m.extensions = _MockExtensions()

    def _setup_ext(name):
        pass

    m.setup_extension.side_effect = _setup_ext

    ret = _mystx_setup(m)
    assert isinstance(ret, dict)
    assert ret == {"parallel_read_safe": True, "parallel_write_safe": True}, ret


def _make_app(configured: list[str] | None = None, loaded: dict | None = None):
    """构造可承受 MySTX 初始化的最小 app mock（extensions 用真实 dict）。"""
    m = MagicMock()

    class _Config:
        extensions = configured if configured is not None else []
        html_theme_options = {}
        release = "0.1.0"

    m.config = _Config()
    m.extensions = dict(loaded or {})
    return m


def test_setup_loads_only_myst_nb_when_chain_undeclared(monkeypatch):
    """回归：myst_nb 在场且用户未声明链上扩展时，仅加载 myst_nb。

    myst_parser 与 myst_nb 共用非幂等 setup_sphinx()（list.remove +
    .md 后缀注册），同时加载在 myst-parser 5.x / Sphinx 9 下必炸。
    """
    import mystx
    from mystx import setup as mystx_setup

    monkeypatch.setattr(mystx, "has_module", lambda name: True)
    app = _make_app()

    mystx_setup(app)

    requested = [c.args[0] for c in app.setup_extension.call_args_list]
    assert "myst_nb" in requested
    assert "myst_parser" not in requested


def test_setup_falls_back_to_myst_parser_without_myst_nb(monkeypatch):
    """未安装 myst_nb 时回退加载 myst_parser（纯主题安装路径）。"""
    import mystx
    from mystx import setup as mystx_setup

    monkeypatch.setattr(mystx, "has_module", lambda name: name != "myst_nb")
    app = _make_app()

    mystx_setup(app)

    requested = [c.args[0] for c in app.setup_extension.call_args_list]
    assert requested == ["myst_parser"]


def test_setup_respects_explicit_chain_declaration(monkeypatch):
    """用户已在 conf 声明链上任一扩展时，mystx 不得再注入。"""
    import mystx
    from mystx import setup as mystx_setup

    monkeypatch.setattr(mystx, "has_module", lambda name: True)

    for declared in ("myst_parser", "myst_nb"):
        app = _make_app(configured=[declared])
        mystx_setup(app)
        requested = [c.args[0] for c in app.setup_extension.call_args_list]
        assert requested == [], f"声明 {declared} 后不应再注入链上扩展，实际：{requested}"

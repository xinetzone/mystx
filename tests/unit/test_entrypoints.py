import inspect
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from sphinx.application import Sphinx
from sphinx.config import Config


def test_entrypoint_imports():
    from mystx.theme import MySTX
    from mystx.config import ConfigManager, config_inited_handler
    from mystx.version_switcher import sphinx_setup as _vss
    from mystx import setup as _mystx_setup

    assert callable(_mystx_setup)


def test_setup_returns_parallel_safe_schema():
    from mystx import setup as _mystx_setup
    from mystx.theme import MySTX
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

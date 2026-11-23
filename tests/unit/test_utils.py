import copy
import importlib.metadata
import importlib.util

import pytest

from mystx.utils import deep_merge, has_module, resolve_release, resolve_site_url


def test_deep_merge_nested_2level():
    base = {"a": {"b": 1}}
    override = {"a": {"c": 2}}
    result = deep_merge(base, override)
    assert result == {"a": {"b": 1, "c": 2}}


def test_deep_merge_remove_marker_none_deletes_key():
    base = {"a": 1, "b": 2}
    override = {"b": None, "c": 3}
    result = deep_merge(base, override, remove_marker=None)
    assert result == {"a": 1, "c": 3}


def test_deep_merge_preserves_base_unmutated():
    base = {"a": {"b": 1}}
    backup = copy.deepcopy(base)
    deep_merge(base, {"a": {"c": 2}})
    assert base == backup


def test_has_module_vs_find_spec():
    expected = importlib.util.find_spec("myst_parser") is not None
    assert has_module("myst_parser") == expected


def test_deep_merge_flat_override():
    base = {"x": 1, "y": 2}
    override = {"y": 99, "z": 3}
    result = deep_merge(base, override)
    assert result == {"x": 1, "y": 99, "z": 3}


def test_has_module_absent_returns_false():
    assert has_module("___definitely_not_a_real_module_xyz___") is False


def test_resolve_release_uses_installed_distribution():
    """已安装的分发包优先于环境变量与兜底值。"""
    installed = importlib.metadata.version("pytest")
    assert resolve_release("pytest", env_var="MYSTX_TEST_VERSION", fallback="0.0.0") == installed


def test_resolve_release_falls_back_to_env(monkeypatch):
    monkeypatch.setenv("MYSTX_TEST_VERSION", "9.9.9")
    assert (
        resolve_release("___no_such_distribution___", env_var="MYSTX_TEST_VERSION", fallback="0.0.0")
        == "9.9.9"
    )


def test_resolve_release_falls_back_to_default(monkeypatch):
    monkeypatch.delenv("MYSTX_TEST_VERSION", raising=False)
    assert resolve_release("___no_such_distribution___", fallback="0.0.0") == "0.0.0"


def test_resolve_release_empty_env_value_is_skipped(monkeypatch):
    """空字符串环境变量不应覆盖兜底值。"""
    monkeypatch.setenv("MYSTX_TEST_VERSION", "")
    assert (
        resolve_release("___no_such_distribution___", env_var="MYSTX_TEST_VERSION", fallback="1.2.3")
        == "1.2.3"
    )


def test_resolve_site_url_returns_none_on_rtd(monkeypatch):
    """RTD 自带 sitemap，包不再注入站点根。"""
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.setenv("READTHEDOCS", "True")
    assert resolve_site_url() is None
    # RTD 不是缺配置，故强校验也不应报错
    assert resolve_site_url(require_on_ci=True) is None


def test_resolve_site_url_prefers_explicit_env(monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("SITEMAP_URL_BASE", "https://xinetzone.github.io/mystx/")
    assert resolve_site_url(require_on_ci=True) == "https://xinetzone.github.io/mystx/"


def test_resolve_site_url_requires_explicit_value_on_ci(monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.delenv("SITEMAP_URL_BASE", raising=False)
    with pytest.raises(RuntimeError, match="SITEMAP_URL_BASE"):
        resolve_site_url(require_on_ci=True)
    # 未开启强校验时退回本地地址（仅本地构建路径）
    assert resolve_site_url() == "http://127.0.0.1:8000/"


def test_resolve_site_url_local_fallback(monkeypatch):
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.delenv("READTHEDOCS", raising=False)
    monkeypatch.delenv("SITEMAP_URL_BASE", raising=False)
    assert resolve_site_url() == "http://127.0.0.1:8000/"

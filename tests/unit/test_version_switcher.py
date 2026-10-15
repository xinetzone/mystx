"""切换下拉（版本/通道切换器）契约测试。

守护四件事——都属「构建期零报错、线上却静默失效」那一类：

1. 清单 ``doc/_static/switcher.json`` 条目合法：pydata 在构建期读它，
   缺 url/version 会 warning；
2. ``version_match`` 按构建环境分流，且**必然落在清单的 version 取值域内**
   ——历史实现会在部分分支返回 ``f"v{release}"`` 这类清单外值，pydata 匹配
   不到任何条目，按钮停在服务端默认文案 "Choose version"；
3. ``switcher.json_url`` 必须是相对路径——绝对 http(s) URL 会让 pydata 在
   构建期发 ``requests.get``，而 CI 的 harden-runner 阻断出网，必然 warning；
4. 以 ``setdefault`` 语义写入 ``html_theme_options``，不覆盖用户显式声明。
"""
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import mystx.version_switcher as vs

_REPO_ROOT = Path(__file__).resolve().parents[2]
_MANIFEST = _REPO_ROOT / "doc" / "_static" / "switcher.json"
_LOCAL_ENV = ("READTHEDOCS", "GITHUB_ACTIONS")


def _entries() -> list[dict[str, str]]:
    return json.loads(_MANIFEST.read_text(encoding="utf-8"))


def _run_setup(monkeypatch, options=None, json_url="_static/switcher.json"):
    """在「本地预览」环境下调用 ``sphinx_setup``，返回 ``(app, config)``。"""
    for var in _LOCAL_ENV:
        monkeypatch.delenv(var, raising=False)
    app = MagicMock()
    config = SimpleNamespace(
        version_switcher_json_url=json_url,
        html_theme_options={} if options is None else options,
    )
    vs.sphinx_setup(app, config)
    return app, config


# -- 清单契约 ---------------------------------------------------------------


def test_manifest_entries_are_wellformed():
    entries = _entries()
    assert entries, "切换清单为空，下拉没有任何可跳转的通道"
    for entry in entries:
        assert entry.get("url"), f"条目缺少 url：{entry}"
        assert entry.get("version"), f"条目缺少 version：{entry}"
        assert entry.get("name"), f"条目缺少 name（按钮正文取的就是它）：{entry}"


def test_channel_constants_match_manifest():
    """代码里的两个通道代号必须真的出现在清单里，否则对应条目永不高亮。"""
    versions = {e["version"] for e in _entries()}
    assert vs.CHANNEL_GH_PAGES in versions, f"{vs.CHANNEL_GH_PAGES!r} 不在清单 {versions} 中"
    assert vs.CHANNEL_RTD in versions, f"{vs.CHANNEL_RTD!r} 不在清单 {versions} 中"


def test_manifest_bases_end_with_slash():
    """pydata 前端拼的是「条目 url + 当前页路径」，基址漏结尾的 / 会拼出坏 URL。"""
    for entry in _entries():
        assert entry["url"].endswith("/"), f"基址未以 / 结尾：{entry['url']}"


# -- 匹配键 -----------------------------------------------------------------


def test_version_match_follows_build_channel(monkeypatch):
    monkeypatch.setenv("READTHEDOCS", "True")
    assert vs.resolve_version_match() == vs.CHANNEL_RTD

    monkeypatch.delenv("READTHEDOCS", raising=False)
    assert vs.resolve_version_match() == vs.CHANNEL_GH_PAGES


def test_version_match_always_names_a_manifest_entry(monkeypatch):
    """两种环境下取到的匹配键都必须能在清单里命中（历史缺陷的直接回归）。"""
    versions = {e["version"] for e in _entries()}
    monkeypatch.setenv("READTHEDOCS", "True")
    assert vs.resolve_version_match() in versions
    monkeypatch.delenv("READTHEDOCS", raising=False)
    assert vs.resolve_version_match() in versions


# -- 数据源 -----------------------------------------------------------------


def test_switcher_json_url_is_relative(monkeypatch):
    _, config = _run_setup(monkeypatch)
    url = config.html_theme_options["switcher"]["json_url"]
    assert not url.startswith(("http://", "https://")), f"不能是绝对 URL：{url}"
    assert (_REPO_ROOT / "doc" / url).is_file(), f"相对路径未指向真实文件：{url}"


def test_repo_conf_points_at_local_manifest():
    """仓库文档站的数据源必须是相对路径，否则 CI（阻断出网）的构建期校验必然 warning。"""
    conf = (_REPO_ROOT / "doc" / "conf.py").read_text(encoding="utf-8")
    assert 'version_switcher_json_url = "_static/switcher.json"' in conf, (
        "doc/conf.py 未把切换清单指向本地文件"
    )


# -- 注入语义 ---------------------------------------------------------------


def test_primary_sidebar_end_keeps_ethical_ads(monkeypatch):
    """覆盖主题默认值时要把伦理广告位带上，否则等于砍掉 RTD 侧的既有行为。"""
    _, config = _run_setup(monkeypatch)
    end = config.html_theme_options["primary_sidebar_end"]
    assert "version-switcher" in end
    assert "sidebar-ethical-ads" in end


def test_user_options_are_not_clobbered(monkeypatch):
    """setdefault 语义：用户显式声明优先（与 apply_book_theme_option_defaults 一致）。"""
    user_options = {
        "switcher": {"json_url": "https://example.com/switcher.json", "version_match": "stable"},
        "primary_sidebar_end": ["version-switcher"],
    }
    _, config = _run_setup(monkeypatch, options=user_options)
    assert config.html_theme_options["switcher"]["json_url"] == "https://example.com/switcher.json"
    assert config.html_theme_options["primary_sidebar_end"] == ["version-switcher"]


def test_blank_json_url_falls_back_to_local_manifest(monkeypatch):
    """空值兜底：json_url 为空会让 pydata 去读来源目录本身，直接抛错。"""
    _, config = _run_setup(monkeypatch, json_url="")
    assert config.html_theme_options["switcher"]["json_url"] == vs.DEFAULT_SWITCHER_JSON


def test_rtd_preview_assets_only_injected_outside_ci(monkeypatch):
    """RTD 样式只在本地预览注入；RTD 与 GitHub Actions 下不注入，避免污染线上产物。"""
    app, _ = _run_setup(monkeypatch)
    assert app.add_css_file.call_count == 2
    assert app.add_js_file.call_count == 1
    assert "rtd-data.js" not in [c.args[0] for c in app.add_js_file.call_args_list], (
        "rtd-data.js 在仓库与主题目录里都不存在，引用它只会让产物多一个 404"
    )

    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    app_ci = MagicMock()
    vs.sphinx_setup(
        app_ci,
        SimpleNamespace(
            version_switcher_json_url=vs.DEFAULT_SWITCHER_JSON,
            html_theme_options={},
        ),
    )
    assert app_ci.add_js_file.call_count == 0

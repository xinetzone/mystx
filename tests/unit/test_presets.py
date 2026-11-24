import pytest

from mystx.config import DEFAULT_MYST_CONFIG
from mystx.presets import (
    apply_site_config,
    build_minimal_myst_config,
    build_mystx_site_config,
    configure_site_fonts,
)
from mystx.presets._shared import build_project_meta, build_setup_closure
from mystx.presets.mystx_site import SiteConfig


def test_minimal_preset_keys_whitelist():
    conf = build_minimal_myst_config({"project": "t", "author": "a", "projecT": "x"})
    assert conf["project"] == "t"
    assert "projecT" not in conf


def test_setup_closure_exec_order():
    calls: list[str] = []

    def reg1(_app):
        calls.append("reg1")

    def reg2(_app):
        calls.append("reg2")

    def user_setup(_app):
        calls.append("user")

    closure = build_setup_closure(
        register_fns=[reg1, reg2],
        user_setup=user_setup,
    )
    closure("dummy_app")
    assert calls == ["reg1", "reg2", "user"]


def test_minimal_extensions_first_item_myst_parser():
    conf = build_minimal_myst_config({"project": "t", "author": "a"})
    assert conf["extensions"][0] == "myst_parser"
    assert conf.get("html_theme") and isinstance(conf["html_theme"], str)
    assert len(conf["html_theme"]) > 0


def test_setup_closure_without_user_setup():
    calls: list[str] = []

    def only_reg(_app):
        calls.append("reg")

    closure = build_setup_closure(register_fns=[only_reg], user_setup=None)
    closure("dummy")
    assert calls == ["reg"]


def test_minimal_preset_has_setup_callable():
    conf = build_minimal_myst_config({"project": "p", "author": "a"})
    assert callable(conf["setup"])


def test_site_preset_core_config():
    values, setup = build_mystx_site_config(site_url="https://example.com/docs/")

    assert values["extensions"][0] == "mystx"
    assert values["html_baseurl"] == "https://example.com/docs/"
    assert values["sitemap_url_scheme"] == "{link}"
    assert values["release"] == values["version"]
    assert values["language"] == "zh_CN"
    assert values["myst_enable_extensions"] == DEFAULT_MYST_CONFIG["myst_enable_extensions"]
    assert values["myst_enable_extensions"] is not DEFAULT_MYST_CONFIG["myst_enable_extensions"]
    assert callable(setup)


def test_site_preset_values_match_declared_contract():
    """取值键集合由 SiteConfig 固定，且钩子不混入取值字典。"""
    values, setup = build_mystx_site_config(site_url=None)

    assert set(values) == set(SiteConfig.__annotations__)
    assert "setup" not in values
    assert callable(setup)


def test_site_config_type_is_type_checking_only():
    """类型契约供类型检查器从门面解析；运行时不建第二个定义，避免 autoapi 重复目标。"""
    import mystx.presets as presets

    assert "SiteConfig" not in presets.__all__
    assert not hasattr(presets, "SiteConfig")


def test_apply_site_config_rejects_undeclared_keys(monkeypatch):
    """键集守卫是最后一道防线：产出未声明键时拒绝注入，且不留下半装配命名空间。"""
    from mystx.presets import mystx_site

    original = mystx_site.build_config

    def _build_with_ghost(**kwargs):
        values, setup = original(**kwargs)
        values["ghost_key"] = True
        return values, setup

    monkeypatch.setattr(mystx_site, "build_config", _build_with_ghost)
    namespace: dict[str, object] = {}

    with pytest.raises(RuntimeError, match="ghost_key"):
        mystx_site.apply_config(namespace, site_url=None)
    assert namespace == {}


def test_project_meta_applies_key_defaults():
    """key_defaults 覆盖分支：站点级默认值优先于通用默认值。"""
    meta = build_project_meta({}, {"html_title": "T", "language": "zh_CN"})

    assert meta["html_title"] == "T"
    assert meta["language"] == "zh_CN"


def test_project_meta_fills_none_theme_options():
    """html_theme_options 为 None 时落为空字典，避免 Sphinx 收到 None。"""
    meta = build_project_meta({})

    assert meta["html_theme_options"] == {}


def test_apply_site_config_injects_values_and_returns_setup():
    """单次调用完成装配：键集合与 SiteConfig 一致，钩子不落进命名空间。"""
    namespace: dict[str, object] = {}
    setup = apply_site_config(namespace, site_url=None)

    assert set(namespace) == set(SiteConfig.__annotations__)
    assert "setup" not in namespace
    assert callable(setup)


def test_docs_profile_injects_fresh_copies(tmp_path):
    """站点画像每次装配都给副本：扩展就地改写字典时不污染模块常量。"""
    from mystx.presets import mystx_docs

    first: dict = {}
    second: dict = {}
    mystx_docs.configure(first, root=tmp_path)
    mystx_docs.configure(second, root=tmp_path)

    assert first["html_theme_options"] is not second["html_theme_options"]
    first["html_theme_options"]["announcement"] = "被改写"
    assert mystx_docs.THEME_OPTIONS["announcement"] != "被改写"


def test_configure_site_fonts_is_explicit_side_effect(tmp_path):
    """字体注册是显式调用的独立副作用，缺目录时静默返回而非抛错。"""
    assert callable(configure_site_fonts)
    configure_site_fonts(tmp_path / "no-such-fonts-dir")


def test_site_preset_without_site_url_disables_sitemap():
    values, _ = build_mystx_site_config(site_url=None)

    assert values["html_baseurl"] == ""
    assert values["sitemap_url_scheme"] == "{lang}{version}{link}"
    assert "sphinx_sitemap" not in values["extensions"]


def test_site_preset_appends_site_increments():
    values, _ = build_mystx_site_config(
        site_url=None,
        nitpick_ignore=(("py:class", "invoke.Collection"),),
        suppress_warnings=("epub.unknown_project_files",),
    )

    assert ("py:class", "invoke.Collection") in values["nitpick_ignore"]
    assert values["suppress_warnings"][-1] == "epub.unknown_project_files"


def test_site_preset_skips_missing_optional_extensions():
    values, _ = build_mystx_site_config(
        site_url=None,
        optional_extensions=("no_such_ext_xyz",),
    )

    assert "no_such_ext_xyz" not in values["extensions"]

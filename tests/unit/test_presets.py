from mystx.config import DEFAULT_MYST_CONFIG
from mystx.presets import build_minimal_myst_config, build_mystx_site_config
from mystx.presets._shared import build_setup_closure


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


def test_site_preset_core_config(tmp_path):
    conf = build_mystx_site_config(root=tmp_path, site_url="https://example.com/docs/")

    assert conf["extensions"][0] == "mystx"
    assert conf["html_baseurl"] == "https://example.com/docs/"
    assert conf["sitemap_url_scheme"] == "{link}"
    assert conf["release"] == conf["version"]
    assert conf["language"] == "zh_CN"
    assert conf["myst_enable_extensions"] == DEFAULT_MYST_CONFIG["myst_enable_extensions"]
    assert conf["myst_enable_extensions"] is not DEFAULT_MYST_CONFIG["myst_enable_extensions"]
    assert callable(conf["setup"])


def test_site_preset_without_site_url_disables_sitemap(tmp_path):
    conf = build_mystx_site_config(root=tmp_path, site_url=None)

    assert conf["html_baseurl"] == ""
    assert conf["sitemap_url_scheme"] == "{lang}{version}{link}"
    assert "sphinx_sitemap" not in conf["extensions"]


def test_site_preset_appends_site_increments(tmp_path):
    conf = build_mystx_site_config(
        root=tmp_path,
        site_url=None,
        nitpick_ignore=(("py:class", "invoke.Collection"),),
        suppress_warnings=("epub.unknown_project_files",),
    )

    assert ("py:class", "invoke.Collection") in conf["nitpick_ignore"]
    assert conf["suppress_warnings"][-1] == "epub.unknown_project_files"


def test_site_preset_skips_missing_optional_extensions(tmp_path):
    conf = build_mystx_site_config(
        root=tmp_path,
        site_url=None,
        optional_extensions=("no_such_ext_xyz",),
    )

    assert "no_such_ext_xyz" not in conf["extensions"]

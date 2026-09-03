from mystx.presets import build_minimal_myst_config
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

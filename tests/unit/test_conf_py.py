"""doc/conf.py 的装配契约测试：确认站点取值显式声明，只剩主题默认值靠事件补齐。

本文件只做「装配面」断言，不启动 Sphinx 构建：目标是把 conf.py 与 ``mystx``
包之间的复用关系固化为机检门禁，避免日后又长回一份隐式注入实现。
"""

import ast
import importlib.util
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from mystx.config import (
    DEFAULT_BUILD_CONFIG,
    DEFAULT_EXT_CONFIG,
    DEFAULT_MYST_CONFIG,
)
from mystx.presets.mystx_site import SITE_CONFIG_SPEC
from mystx.themes import BOOK_THEME_NAMES

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


def test_conf_declares_identity_and_early_keys():
    """身份与早读键直接写在模块层，取值明确可读。"""
    conf = _load_conf()

    assert (conf.project, conf.author, conf.copyright) == ("mystx", "xinetzone", "2026, xinetzone")
    # 早读键必须在模块层就位
    assert conf.extensions[0] == "mystx"
    assert conf.language == "zh_CN"
    assert conf.locale_dirs == ["../locales/"]
    assert conf.gettext_compact is False
    assert conf.version == conf.release


def test_conf_covers_every_site_config_key():
    """机制声明过的键在 conf.py 都有同名取值：不存在依赖注入的缺口。"""
    conf = _load_conf()

    missing = sorted(set(SITE_CONFIG_SPEC) - set(dir(conf)))
    assert not missing, f"conf.py 缺少取值: {missing}"
    # 事件注入的实现痕迹已移除
    for name in ("_values", "_apply_profile", "_EXPLICIT_KEYS", "assemble_site_config"):
        assert not hasattr(conf, name), name


def test_conf_values_match_package_defaults():
    """与包内默认值同源的键取值一致；配置层不另立第二套默认值。"""
    conf = _load_conf()

    assert conf.html_theme in BOOK_THEME_NAMES
    assert conf.numfig == DEFAULT_BUILD_CONFIG["numfig"]
    assert conf.myst_enable_extensions == DEFAULT_MYST_CONFIG["myst_enable_extensions"]
    assert conf.copybutton_exclude == DEFAULT_EXT_CONFIG["copybutton_exclude"]
    assert conf.copybutton_selector == DEFAULT_EXT_CONFIG["copybutton_selector"]
    # 站点层只声明覆盖项；主题默认值由 mystx 在 config-inited 补齐
    assert set(conf.html_theme_options) == {
        "announcement",
        "repository_url",
        "icon_links",
        "launch_buttons",
    }
    assert conf.html_theme_options["icon_links"] == conf._icon_links()


def test_conf_imports_from_mystx_use_private_aliases():
    """包内导入必须以下划线别名引入：conf 的命名空间就是 Sphinx 的配置空间。

    与配置键同名的导入会被 ``Config`` 直接读成取值（``intersphinx_mapping``
    曾因此把函数对象写进配置），构建期不报错、只在消费端以怪异形式暴露。
    """
    tree = ast.parse(CONF_PATH.read_text(encoding="utf-8"))
    offenders = [
        alias.asname or alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and (node.module or "").split(".")[0] == "mystx"
        for alias in node.names
        if not (alias.asname or alias.name).startswith("_")
    ]
    assert not offenders, f"以下导入会占用配置命名空间: {offenders}"


def test_conf_setup_registers_docs_directives_and_parallel_guard():
    _require_upstream_docs()
    conf = _load_conf()
    app = MagicMock()

    meta = conf.setup(app)

    registered = [call.args[0] for call in app.add_directive.call_args_list]
    assert "myst-config" in registered
    assert "myst-example" in registered
    # 只连接并行守卫；不再有 config-inited 补写
    events = [call.args[0] for call in app.connect.call_args_list]
    assert events == ["env-before-read-docs"]
    assert meta["version"] == conf.release
    assert meta["parallel_read_safe"] is True

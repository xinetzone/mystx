"""``ConfigManager`` 的顶层键合并契约：``_config.toml`` 非主题键直接写入 Config。"""
import logging
from pathlib import Path
from types import SimpleNamespace

from mystx.config.runtime import ConfigManager


def _manager(tmp_path: Path, toml_text: str):
    (tmp_path / "_config.toml").write_text(toml_text, encoding="utf-8")
    app = SimpleNamespace(srcdir=str(tmp_path))
    config = SimpleNamespace(html_theme_options={}, values={"html_title": None, "project": None})
    return ConfigManager(app=app, config=config)


def test_toplevel_keys_are_applied_and_theme_options_merged(tmp_path):
    manager = _manager(
        tmp_path,
        'html_title = "T"\nproject = "p"\n[html_theme_options]\nannouncement = "a"\n',
    )

    manager.apply_config()

    assert manager.config.html_title == "T"
    assert manager.config.project == "p"
    assert manager.config.html_theme_options == {"announcement": "a"}


def test_unknown_key_warns_and_is_skipped(tmp_path, caplog):
    manager = _manager(tmp_path, 'mystx_unknown = 1\n')

    with caplog.at_level(logging.WARNING):
        manager.apply_config()

    assert not hasattr(manager.config, "mystx_unknown")
    assert "mystx_unknown" in caplog.text
    assert "已跳过" in caplog.text


def test_unknown_keys_are_aggregated_with_structured_type(tmp_path, caplog):
    manager = _manager(tmp_path, 'mystx_beta = 2\nmystx_alpha = 1\n')

    with caplog.at_level(logging.WARNING):
        manager.apply_config()

    records = [r for r in caplog.records if getattr(r, "type", "") == "config"]
    assert len(records) == 1
    record = records[0]
    assert record.subtype == "unknown_key"
    message = record.getMessage()
    assert "2 个键" in message
    assert "mystx_alpha、mystx_beta" in message
    assert not hasattr(manager.config, "mystx_alpha")
    assert not hasattr(manager.config, "mystx_beta")

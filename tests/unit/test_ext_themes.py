import pytest

from mystx.extensions import resolve_extensions
from mystx.themes import resolve_theme, resolve_theme_options


def test_resolve_theme_returns_mystx():
    assert resolve_theme() == "mystx"


def test_resolve_theme_options_injects_defaults():
    opts = resolve_theme_options(
        "mystx",
        {"path_to_docs": "docs-overridden"},
    )
    assert "use_repository_button" in opts
    assert opts["path_to_docs"] == "docs-overridden"


def test_resolve_extensions_missing_required_raises():
    with pytest.raises(ImportError) as excinfo:
        resolve_extensions(required=("__absent__",))
    assert "[mystx.extensions]" in str(excinfo.value)


def test_resolve_theme_alabaster_fallback():
    theme = resolve_theme(priority=("__no_such_theme_xyz__",), extra_before=(), extra_after=())
    assert theme == "alabaster"


def test_resolve_theme_options_override_multiple():
    opts = resolve_theme_options(
        "mystx",
        {"use_repository_button": False, "repository_branch": "dev"},
    )
    assert opts["use_repository_button"] is False
    assert opts["repository_branch"] == "dev"
    assert opts["use_source_button"] is True

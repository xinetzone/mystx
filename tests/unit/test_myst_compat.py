import pytest
from docutils import nodes

from mystx.myst_compat import (
    _reload_env_settings,
    dedupe_injected_h1,
    quote_frontmatter_dates,
)


@pytest.fixture(autouse=True)
def _fresh_env_settings(monkeypatch):
    monkeypatch.delenv("MYSTX_MYST_COMPAT_QUOTE_DATES", raising=False)
    monkeypatch.delenv("MYSTX_MYST_COMPAT_DEDUPE_H1", raising=False)
    monkeypatch.delenv("SW_MYST_COMPAT_QUOTE_DATES", raising=False)
    monkeypatch.delenv("SW_MYST_COMPAT_DEDUPE_H1", raising=False)
    _reload_env_settings()
    yield
    _reload_env_settings()


def test_quote_frontmatter_dates_yml():
    source = ["---\ndate: 2026-09-03\ntitle: Hello\n---\n\nbody\n"]
    quote_frontmatter_dates(None, "test", source)
    assert 'date: "2026-09-03"' in source[0]


def test_quote_frontmatter_dates_toml_not_modified():
    original = "+++\ndate = 2026-09-03\ntitle = \"Hello\"\n+++\n\nbody\n"
    source = [original]
    quote_frontmatter_dates(None, "test", source)
    assert source[0] == original


def test_dedupe_injected_h1_removes_only_first_sec():
    doctree = nodes.document({}, {})
    sec1 = nodes.section()
    sec1.append(nodes.title(text="Injected"))
    sec2 = nodes.section()
    sec2.append(nodes.title(text="Real H1"))
    sec2.append(nodes.paragraph(text="body content"))
    doctree.append(sec1)
    doctree.append(sec2)

    dedupe_injected_h1(None, doctree)

    sections = [n for n in doctree.children if isinstance(n, nodes.section)]
    assert len(sections) == 1
    assert sections[0].children[0].astext() == "Real H1"


def test_env_turnoff_quote(monkeypatch):
    monkeypatch.setenv("MYSTX_MYST_COMPAT_QUOTE_DATES", "0")
    _reload_env_settings()
    original = "---\ndate: 2026-09-03\ntitle: Hello\n---\n\nbody\n"
    source = [original]
    quote_frontmatter_dates(None, "test", source)
    assert source[0] == original


def test_sw_alias_works_and_emits_deprecation_log(monkeypatch, caplog):
    monkeypatch.setenv("SW_MYST_COMPAT_DEDUPE_H1", "0")
    with caplog.at_level("INFO"):
        _reload_env_settings()
    deprecation_records = [r for r in caplog.records if "Deprecated" in r.getMessage()]
    assert len(deprecation_records) >= 1

    doctree = nodes.document({}, {})
    sec1 = nodes.section()
    sec1.append(nodes.title(text="Injected"))
    sec2 = nodes.section()
    sec2.append(nodes.title(text="Real H1"))
    sec2.append(nodes.paragraph(text="body content"))
    doctree.append(sec1)
    doctree.append(sec2)

    dedupe_injected_h1(None, doctree)

    sections = [n for n in doctree.children if isinstance(n, nodes.section)]
    assert len(sections) == 2


def test_quote_frontmatter_datetime_with_timezone():
    source = ["---\ndate: 2026-09-03T10:30:00+08:00\n---\n\nbody\n"]
    quote_frontmatter_dates(None, "test", source)
    assert 'date: "2026-09-03T10:30:00+08:00"' in source[0]


def test_no_frontmatter_no_change():
    original = "# No FM\n\nJust a regular doc.\n"
    source = [original]
    quote_frontmatter_dates(None, "test", source)
    assert source[0] == original

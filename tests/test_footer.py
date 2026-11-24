"""内容页脚测试：条目数据、缺数据跳过与回退基座。"""

from __future__ import annotations

from io import StringIO
from textwrap import dedent

from sphinx.application import Sphinx
from sphinx.util.docutils import docutils_namespace

from mystx.book.footer import build_footer

CONTEXT = {"author": "xinetzone", "copyright": "2026, xinetzone", "last_updated": "2026-11-24"}


def types(items):
    return [item["type"] for item in items]


def test_default_order():
    items = build_footer(CONTEXT, ["author", "copyright", "last-updated"])
    assert types(items) == ["author", "copyright", "last-updated"]
    assert items[1]["text"] == "2026, xinetzone"


def test_missing_values_are_skipped():
    items = build_footer({"author": "xinetzone"}, ["author", "copyright", "last-updated"])
    assert types(items) == ["author"]


def test_unknown_names_are_ignored():
    assert build_footer(CONTEXT, ["bogus", "author"]) == [
        {"type": "author", "text": "xinetzone"}
    ]


def test_empty_config_renders_no_items():
    assert build_footer(CONTEXT, []) == []


def build_site(tmp_path, *, options: dict) -> str:
    src = tmp_path / "src"
    src.mkdir()
    (src / "index.rst").write_text(dedent("""
            Home
            ====

            Body.
            """), encoding="utf-8")
    (src / "conf.py").write_text(
        "extensions = ['mystx']\n"
        "html_theme = 'mystx'\n"
        "exclude_patterns = ['_build']\n"
        "author = 'xinetzone'\n"
        "copyright = '2026, xinetzone'\n"
        "html_last_updated_fmt = '%Y-%m-%d'\n"
        f"html_theme_options = {options!r}\n",
        encoding="utf-8",
    )
    with docutils_namespace():
        app = Sphinx(
            srcdir=str(src),
            confdir=str(src),
            outdir=str(tmp_path / "out"),
            doctreedir=str(tmp_path / "doctrees"),
            buildername="html",
            warning=StringIO(),
            freshenv=True,
            warningiserror=True,
        )
        app.build()
    return (tmp_path / "out" / "index.html").read_text(encoding="utf-8")


def test_footer_renders_items(tmp_path):
    html = build_site(tmp_path, options={"book_footer_items": ["author", "copyright", "last-updated"]})
    assert "book-footer__author" in html
    assert "book-footer__copyright" in html
    assert "book-footer__last-updated" in html
    assert "xinetzone" in html


def test_footer_order_comes_from_config(tmp_path):
    html = build_site(tmp_path, options={"book_footer_items": ["last-updated", "author"]})
    assert html.index("book-footer__last-updated") < html.index("book-footer__author")


def test_empty_footer_falls_back_to_base(tmp_path):
    html = build_site(tmp_path, options={"book_footer_items": []})
    assert "book-footer__item" not in html
    assert "sphinx-version" in html

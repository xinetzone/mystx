"""边注测试：脚注转边注、margin 指令、嵌套副本与开关回退。"""

from __future__ import annotations

from io import StringIO
from textwrap import dedent

import pytest
from sphinx.application import Sphinx

PAGES = {
    "index.rst": """
        Notes
        =====

        Body text with a note [1]_ and a margin note [2]_.

        .. note::

           Inside an admonition there is a note [3]_.

        .. [1] Plain sidenote body.
        .. [2] {-}Margin note body.
        .. [3] Nested footnote body.
        """,
    "block.rst": """
        Block
        =====

        .. margin:: Margin title

           Block content stays in the margin.
        """,
    "quiet.rst": """
        Quiet
        =====

        A page without footnotes.
        """,
}

DEFAULT_OPTIONS = {"book_use_sidenotes": True}


def build(tmp_path, *, options: dict | None = None) -> str:
    src = tmp_path / "src"
    src.mkdir()
    for name, body in PAGES.items():
        path = src / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(dedent(body), encoding="utf-8")

    (src / "conf.py").write_text(
        "extensions = ['mystx']\n"
        "html_theme = 'mystx'\n"
        "exclude_patterns = ['_build']\n"
        f"html_theme_options = {options!r}\n",
        encoding="utf-8",
    )

    warning = StringIO()
    app = Sphinx(
        srcdir=str(src),
        confdir=str(src),
        outdir=str(tmp_path / "out"),
        doctreedir=str(tmp_path / "doctrees"),
        buildername="html",
        warning=warning,
        freshenv=True,
        warningiserror=True,
    )
    app.build()
    return (tmp_path / "out").as_posix()


def read(out: str, page: str) -> str:
    with open(f"{out}/{page}", encoding="utf-8") as handle:
        return handle.read()


def article(html: str) -> str:
    start = html.index("<article")
    return html[start : html.index("</article>", start)]


def test_footnote_becomes_sidenote(tmp_path):
    html = read(build(tmp_path, options=DEFAULT_OPTIONS), "index.html")
    assert 'class="sidenote"' in html
    assert 'class="margin-toggle"' in html
    assert "Plain sidenote body." in html
    # 原脚注已被删除，页尾不再有脚注区
    assert "footnote-list" not in html


def test_margin_marker_drops_number(tmp_path):
    html = read(build(tmp_path, options=DEFAULT_OPTIONS), "index.html")
    assert 'class="marginnote"' in html
    assert "marginnote-role-2" in html
    assert "{-}" not in article(html)


def test_margin_directive_becomes_margin_block(tmp_path):
    html = read(build(tmp_path, options=DEFAULT_OPTIONS), "block.html")
    assert "margin sidebar" in html
    assert "Margin title" in html
    assert "Block content stays in the margin." in html


def test_nested_reference_keeps_narrow_copy(tmp_path):
    html = article(read(build(tmp_path, options=DEFAULT_OPTIONS), "index.html"))
    assert "sidenote d-n" in html
    # 宽屏副本被提到提示框之外，窄屏副本留在容器内
    assert html.index("Nested footnote body.") < html.index("sidenote d-n")


def test_margin_content_flags_body_class(tmp_path):
    out = build(tmp_path, options=DEFAULT_OPTIONS)
    assert "mystx-has-margin" in read(out, "index.html")
    assert "mystx-has-margin" in read(out, "block.html")
    assert "mystx-has-margin" not in read(out, "quiet.html")


def test_margin_directive_works_without_switch(tmp_path):
    html = read(build(tmp_path, options={}), "block.html")
    assert "margin sidebar" in html
    assert "margin-toggle" not in html


@pytest.mark.parametrize("options", [{}, {"book_use_sidenotes": False}])
def test_switch_off_keeps_plain_footnotes(tmp_path, options):
    html = read(build(tmp_path, options=options), "index.html")
    assert "margin-toggle" not in html
    assert "footnote-list" in html
    assert "mystx-has-margin" not in html

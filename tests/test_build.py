"""主题构建测试：用最小站点验证书籍导航与基座中和。"""

from __future__ import annotations

from io import StringIO
from textwrap import dedent

import pytest
from sphinx.application import Sphinx

PAGES = {
    "index.rst": """
        PoC
        ===

        .. toctree::
           :maxdepth: 2

           guide/index
           api
        """,
    "guide/index.rst": """
        Guide
        =====

        .. toctree::

           setup
           deep
        """,
    "guide/setup.rst": "Setup\n=====\n",
    "guide/deep.rst": "Deep\n====\n",
    "api.rst": "API\n===\n",
}


def build_site(tmp_path, *, options: dict | None = None) -> str:
    src = tmp_path / "src"
    src.mkdir()
    for name, body in PAGES.items():
        path = src / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(dedent(body), encoding="utf-8")

    extra = repr(options or {})
    (src / "conf.py").write_text(
        "extensions = ['mystx']\n"
        "html_theme = 'mystx'\n"
        "exclude_patterns = ['_build']\n"
        f"html_theme_options = {extra}\n",
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


@pytest.mark.parametrize("page", ["index.html", "guide/setup.html"])
def test_book_nav_renders_whole_tree(tmp_path, page):
    out = build_site(tmp_path)
    html = open(f"{out}/{page}", encoding="utf-8").read()
    for title in (">Guide<", ">Setup<", ">Deep<", ">API<"):
        assert title in html
    assert "mystx-book-nav" in html


def test_current_page_is_marked(tmp_path):
    out = build_site(tmp_path)
    html = open(f"{out}/guide/setup.html", encoding="utf-8").read()
    assert "aria-current" in html


def test_navbar_is_neutralized(tmp_path):
    out = build_site(tmp_path)
    html = open(f"{out}/guide/setup.html", encoding="utf-8").read()
    assert "navbar-nav" not in html


def test_css_and_content_width_are_injected(tmp_path):
    out = build_site(tmp_path)
    html = open(f"{out}/index.html", encoding="utf-8").read()
    assert "css/book.css" in html
    assert "--mystx-content-width" in html


def test_section_scope_hides_other_chapters(tmp_path):
    out = build_site(tmp_path, options={"book_nav_scope": "section"})
    html = open(f"{out}/guide/setup.html", encoding="utf-8").read()
    assert ">Guide<" in html
    assert ">Setup<" in html
    assert ">API<" not in html

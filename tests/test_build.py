"""主题构建测试：用最小站点验证书籍导航与基座中和。"""

from __future__ import annotations

from io import StringIO
from textwrap import dedent

import pytest
from sphinx.application import Sphinx
from sphinx.util.docutils import docutils_namespace

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


def build_site(tmp_path, *, options: dict | None = None, context: dict | None = None) -> str:
    src = tmp_path / "src"
    src.mkdir()
    for name, body in PAGES.items():
        path = src / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(dedent(body), encoding="utf-8")

    extra = repr(options or {})
    html_context = repr(context or {})
    (src / "conf.py").write_text(
        "extensions = ['mystx']\n"
        "html_theme = 'mystx'\n"
        "exclude_patterns = ['_build']\n"
        f"html_theme_options = {extra}\n"
        f"html_context = {html_context}\n",
        encoding="utf-8",
    )

    warning = StringIO()
    with docutils_namespace():
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


def test_sidebar_collapses_other_chapters(tmp_path):
    out = build_site(tmp_path)
    html = open(f"{out}/guide/setup.html", encoding="utf-8").read()
    nav = html[html.index("mystx-book-nav") : html.index("</nav>")]
    # 默认只展开顶层：当前章节打开，其余章节折叠
    assert nav.count('open="open"') == 1
    assert "<details open" not in nav[nav.index(">API<") :]


def test_no_toc_page_is_marked_for_left_alignment(tmp_path):
    out = build_site(tmp_path)
    html = open(f"{out}/guide/index.html", encoding="utf-8").read()
    # 分区首页只有目录，没有页内标题：基座不渲染右侧目录栏
    assert 'class="mystx-no-toc"' in html


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


def test_header_buttons_without_repo(tmp_path):
    out = build_site(tmp_path)
    html = open(f"{out}/guide/setup.html", encoding="utf-8").read()
    assert "book-header-buttons" in html
    assert "toggleFullscreen()" in html
    assert "issues/new" not in html


def test_header_buttons_with_repo(tmp_path):
    out = build_site(
        tmp_path,
        context={
            "github_user": "acme",
            "github_repo": "docs",
            "github_version": "main",
            "doc_path": "doc",
        },
    )
    html = open(f"{out}/guide/setup.html", encoding="utf-8").read()
    assert "https://github.com/acme/docs/edit/main/doc/guide/setup.rst" in html
    assert "https://github.com/acme/docs/blob/main/doc/guide/setup.rst?plain=1" in html
    assert "https://github.com/acme/docs/issues/new" in html
    assert "js/book.js" in html

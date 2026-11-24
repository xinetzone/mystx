"""MyST 站点兼容测试：Markdown 源文件走同一套主题能力。"""

from __future__ import annotations

from io import StringIO
from textwrap import dedent

import pytest

pytest.importorskip("myst_parser", reason="未安装 myst-parser")

from sphinx.application import Sphinx  # noqa: E402
from sphinx.util.docutils import docutils_namespace  # noqa: E402

PAGES = {
    "index.md": """
        # MyST Site

        ```{toctree}
        :maxdepth: 2

        guide/index
        ```
        """,
    "guide/index.md": """
        # Guide

        ```{toctree}

        notes
        ```
        """,
    "guide/notes.md": """
        # Notes

        正文里的引用点[^n1]。

        ```{margin} 旁注标题
        块级留白内容。
        ```

        ## 小节

        普通段落。

        [^n1]: 这条脚注应当变成边注。
        """,
}


def build_myst_site(tmp_path, *, options: dict | None = None) -> str:
    src = tmp_path / "src"
    src.mkdir()
    for name, body in PAGES.items():
        path = src / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(dedent(body), encoding="utf-8")

    (src / "conf.py").write_text(
        "extensions = ['mystx', 'myst_parser']\n"
        "html_theme = 'mystx'\n"
        "exclude_patterns = ['_build']\n"
        f"html_theme_options = {options or {}!r}\n",
        encoding="utf-8",
    )

    warning = StringIO()
    # docutils_namespace 隔离全局指令/角色注册表：同一进程多次建站时不互相污染
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
    assert not warning.getvalue(), warning.getvalue()
    return (tmp_path / "out").as_posix()


def test_markdown_pages_build_with_book_nav(tmp_path):
    out = build_myst_site(tmp_path)
    html = open(f"{out}/guide/notes.html", encoding="utf-8").read()
    assert ">Notes<" in html
    assert "mystx-book-nav" in html
    assert ">Guide<" in html


def test_markdown_footnote_becomes_sidenote(tmp_path):
    out = build_myst_site(tmp_path, options={"book_use_sidenotes": True})
    html = open(f"{out}/guide/notes.html", encoding="utf-8").read()
    assert 'class="margin-toggle"' in html
    assert "sidenote" in html
    assert "mystx-has-margin" in html
    # 脚注正文已搬进边注，页底不再留脚注列表
    assert "footnote-list" not in html


def test_markdown_margin_directive_becomes_margin_block(tmp_path):
    out = build_myst_site(tmp_path)
    html = open(f"{out}/guide/notes.html", encoding="utf-8").read()
    assert "旁注标题" in html
    assert 'class="margin' in html
    assert "mystx-has-margin" in html


def test_sidenotes_off_keeps_markdown_footnote_native(tmp_path):
    out = build_myst_site(tmp_path)
    html = open(f"{out}/guide/notes.html", encoding="utf-8").read()
    assert 'class="margin-toggle"' not in html
    assert "footnote-list" in html

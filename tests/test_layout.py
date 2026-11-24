"""布局类名：页面结构决定 ``<body>`` 上的 class。"""

from __future__ import annotations

from mystx.book.options import body_classes


def test_no_toc_page_is_marked():
    assert body_classes({}, has_margin=False) == "mystx-no-toc"


def test_toc_page_keeps_base_layout():
    assert body_classes({"display_toc": True}, has_margin=False) == ""


def test_margin_page_combines_both_classes():
    assert body_classes({}, has_margin=True) == "mystx-has-margin mystx-no-toc"


def test_margin_page_with_toc_only_has_margin():
    assert body_classes({"display_toc": True}, has_margin=True) == "mystx-has-margin"

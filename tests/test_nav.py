"""侧栏参数纯函数测试。"""

import pytest

from mystx.book.nav import sidebar_kwargs


def test_book_scope_starts_at_root():
    kw = sidebar_kwargs("book", depth=3, maxdepth=4)
    assert kw.startdepth == 0
    assert kw.show_nav_level == 3
    assert kw.maxdepth == 4
    assert kw.includehidden is True
    assert kw.titles_only is True


def test_section_scope_starts_at_child_level():
    assert sidebar_kwargs("section", depth=1, maxdepth=2).startdepth == 1


def test_depth_is_clamped_to_positive():
    kw = sidebar_kwargs("book", depth=0, maxdepth=0)
    assert kw.show_nav_level == 1
    assert kw.maxdepth == 1


def test_unknown_scope_raises():
    with pytest.raises(ValueError):
        sidebar_kwargs("page", depth=1, maxdepth=1)

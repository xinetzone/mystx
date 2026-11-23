"""mystx.ext.gallery 的单元测试：注册契约、选项声明与卡片拼装。"""
from unittest.mock import MagicMock

from mystx.ext.gallery import GalleryGridDirective, _as_options, _card_body, setup


def test_setup_registers_gallery_grid():
    app = MagicMock()

    meta = setup(app)

    app.add_directive.assert_called_once_with("gallery-grid", GalleryGridDirective)
    assert meta == {"parallel_read_safe": True, "parallel_write_safe": True}


def test_directive_contract():
    assert GalleryGridDirective.name == "gallery-grid"
    assert GalleryGridDirective.has_content is True
    assert GalleryGridDirective.optional_arguments == 1
    assert set(GalleryGridDirective.option_spec) == {
        "grid-columns",
        "class-container",
        "class-card",
    }


def test_card_body_keeps_header_image_content_order():
    item = {"header": "H", "image": "i.png", "content": "C", "class-card": "x"}

    body = _card_body(item)

    assert body == "H  \n^^^  \n![image](i.png)  \nC  \n"
    # 只消费正文三键，其余键留给 grid-item-card 选项
    assert item == {"class-card": "x"}


def test_card_body_skips_missing_parts():
    assert _card_body({"content": "C"}) == "C  \n"
    assert _card_body({"header": "H"}) == "H  \n^^^  \n"
    assert _card_body({}) == ""


def test_as_options_renders_directive_lines():
    assert _as_options({"gutter": 2, "class-container": "gallery-directive"}) == (
        ":gutter: 2\n:class-container: gallery-directive"
    )

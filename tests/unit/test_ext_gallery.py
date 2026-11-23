"""mystx.ext.gallery 的单元测试：注册契约与指令选项声明。"""
from unittest.mock import MagicMock

from mystx.ext.gallery import GalleryGridDirective, setup


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

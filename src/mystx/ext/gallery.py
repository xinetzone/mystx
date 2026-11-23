"""``gallery-grid`` 指令：由结构化数据生成等宽图片画廊。

文档站里「一排等宽、带标题与链接的卡片」是高频版式，手写容易错行且难以
批量维护。本指令把该版式收敛为一条指令：接受 YAML 列表（写在指令体内，
或给出指向 YAML 文件的参数），逐项展开为 sphinx-design 的
``grid`` + ``grid-item-card``。

用法（MyST）::

    ```{gallery-grid}
    :grid-columns: 1 2 3
    - header: 项目名
      image: https://example.org/logo.png
      content: 一句话说明
    ```

迁移说明：本模块原为 ``doc/_ext/gallery_directive.py``（源自
pydata-sphinx-theme 的维护者工具），迁入包内后下游项目无需再把 ``doc/``
插入 ``sys.path``，直接以 ``mystx.ext.gallery`` 加入 ``extensions`` 即可。
"""

from pathlib import Path
from typing import Any, ClassVar

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.application import Sphinx
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective
from yaml import safe_load

logger = logging.getLogger(__name__)

TEMPLATE_GRID = """
`````{{grid}} {columns}
{options}

{content}

`````
"""

GRID_CARD = """
````{{grid-item-card}} {title}
{options}

{content}
````
"""


class GalleryGridDirective(SphinxDirective):
    """把 YAML 描述的画廊展开为 sphinx-design 卡片网格。

    该项内容可以是 YAML 文件路径（作为指令参数给出，相对当前文档解析），
    也可以直接写在指令体内。每个列表项可含 ``title`` / ``header`` /
    ``image`` / ``content`` 以及任意 ``grid-item-card`` 选项。

    注意：生成的模板是 Markdown 语法，因此本指令只能用于 MyST 页面。
    """

    name = "gallery-grid"
    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec: ClassVar[dict[str, Any]] = {
        # A class to be added to the resulting container
        "grid-columns": directives.unchanged,
        "class-container": directives.unchanged,
        "class-card": directives.unchanged,
    }

    def run(self) -> list[nodes.Node]:
        """Create the gallery grid."""
        if self.arguments:
            # If an argument is given, assume it's a path to a YAML file
            # Parse it and load it into the directive content
            path_data_rel = Path(self.arguments[0])
            path_doc, _ = self.get_source_info()
            path_doc = Path(path_doc).parent
            path_data = (path_doc / path_data_rel).resolve()
            if not path_data.exists():
                logger.warning("Could not find grid data at %s.", path_data)
                return [nodes.paragraph("", f"Could not find grid data at {path_data}.")]
            yaml_string = path_data.read_text()
        else:
            yaml_string = "\n".join(self.content)

        # Use all the element with an img-bottom key as sites to show
        # and generate a card item for each of them
        grid_items = []
        for item in safe_load(yaml_string):
            # remove parameters that are not needed for the card options
            title = item.pop("title", "")

            # build the content of the card using some extra parameters
            header = f"{item.pop('header')}  \n^^^  \n" if "header" in item else ""
            image = f"![image]({item.pop('image')})  \n" if "image" in item else ""
            content = f"{item.pop('content')}  \n" if "content" in item else ""

            # optional parameter that influence all cards
            if "class-card" in self.options:
                item["class-card"] = self.options["class-card"]

            loc_options_str = "\n".join(f":{k}: {v}" for k, v in item.items()) + "  \n"

            card = GRID_CARD.format(
                options=loc_options_str, content=header + image + content, title=title
            )
            grid_items.append(card)

        # Parse the template with Sphinx Design to create an output container
        # Prep the options for the template grid
        class_ = "gallery-directive" + f' {self.options.get("class-container", "")}'
        options = {"gutter": 2, "class-container": class_}
        options_str = "\n".join(f":{k}: {v}" for k, v in options.items())

        # Create the directive string for the grid
        grid_directive = TEMPLATE_GRID.format(
            columns=self.options.get("grid-columns", "1 2 3 4"),
            options=options_str,
            content="\n".join(grid_items),
        )

        # Parse content as a directive so Sphinx Design processes it
        container = nodes.container()
        self.state.nested_parse([grid_directive], 0, container)

        # Sphinx Design outputs a container too, so just use that
        return [container.children[0]]


def setup(app: Sphinx) -> dict[str, Any]:
    """注册 ``gallery-grid`` 指令。

    Returns:
        扩展元信息，读写两阶段均声明并行安全。
    """
    app.add_directive("gallery-grid", GalleryGridDirective)

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }

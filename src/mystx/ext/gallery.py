"""``gallery-grid`` 指令：由结构化 YAML 生成等宽卡片画廊。

把「一排等宽、带标题与链接的卡片」收敛为一条 MyST 指令：接受 YAML 列表
（写在指令体内，或给出指向 YAML 文件的参数），逐项展开为 sphinx-design 的
``grid`` + ``grid-item-card``。原为 ``doc/_ext/gallery_directive.py``，迁入包内
后下游无需再把 ``doc/`` 插入 ``sys.path``。

用法::

    ```{gallery-grid}
    :grid-columns: 1 2 3
    - header: 项目名
      image: https://example.org/logo.png
      content: 一句话说明
    ```
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


def _as_options(mapping: dict[str, Any]) -> str:
    """把 ``{选项: 值}`` 渲染为 sphinx-design 的 ``:选项: 值`` 行。"""
    return "\n".join(f":{key}: {value}" for key, value in mapping.items())


def _card_body(item: dict[str, Any]) -> str:
    """按 header → image → content 组装卡片正文，缺项跳过。

    就地消费这三个键，使剩余键自然成为 ``grid-item-card`` 选项。
    """
    parts = []
    if header := item.pop("header", None):
        parts.append(f"{header}  \n^^^  ")
    if image := item.pop("image", None):
        parts.append(f"![image]({image})  ")
    if content := item.pop("content", None):
        parts.append(f"{content}  ")
    return "".join(f"{part}\n" for part in parts)


class GalleryGridDirective(SphinxDirective):
    """把 YAML 描述的画廊展开为卡片网格（仅适用于 MyST 页面）。"""

    name = "gallery-grid"
    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec: ClassVar[dict[str, Any]] = {
        "grid-columns": directives.unchanged,  # 每行列数，如 "1 2 3"
        "class-container": directives.unchanged,  # 追加到网格容器的类
        "class-card": directives.unchanged,  # 追加到每张卡片的类
    }

    def run(self) -> list[nodes.Node]:
        """解析 YAML 并生成网格容器节点。"""
        if self.arguments:
            path_doc, _ = self.get_source_info()
            path_data = (Path(path_doc).parent / self.arguments[0]).resolve()
            if not path_data.exists():
                message = f"Could not find grid data at {path_data}."
                logger.warning(message)
                return [nodes.paragraph("", message)]
            yaml_string = path_data.read_text()
        else:
            yaml_string = "\n".join(self.content)

        cards = []
        for item in safe_load(yaml_string):
            title = item.pop("title", "")
            body = _card_body(item)
            if "class-card" in self.options:
                item["class-card"] = self.options["class-card"]
            cards.append(
                GRID_CARD.format(
                    options=_as_options(item) + "  \n",
                    content=body,
                    title=title,
                )
            )

        container_class = " ".join(
            part
            for part in ("gallery-directive", self.options.get("class-container", ""))
            if part
        )
        grid = TEMPLATE_GRID.format(
            columns=self.options.get("grid-columns", "1 2 3 4"),
            options=_as_options({"gutter": 2, "class-container": container_class}),
            content="\n".join(cards),
        )

        # 交给 Sphinx Design 解析：它会产出自己的容器，直接取其子节点
        container = nodes.container()
        self.state.nested_parse([grid], 0, container)
        return [container.children[0]]


def setup(app: Sphinx) -> dict[str, Any]:
    """注册 ``gallery-grid`` 指令；读写两阶段均声明并行安全。"""
    app.add_directive("gallery-grid", GalleryGridDirective)
    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }

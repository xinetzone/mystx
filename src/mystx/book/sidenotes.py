"""边注：脚注转侧栏注释，以及 ``{margin}`` 块级留白指令。

结构与策略参考 sphinx-book-theme（BSD-3-Clause，Copyright (c) Executable Book
Project）的 ``SideNoteNode`` / ``HandleFootnoteTransform`` / ``Margin``，并按
mystx 的选项命名与失败姿态重写：

- 开关是 ``book_use_sidenotes``，默认关闭；关闭时脚注保持原生行为。
- 脚注找不到正文、或引用找不到对应脚注时跳过该条，不抛异常。
- ``{margin}`` 指令与样式常驻，开关只控制脚注变换。
"""

from __future__ import annotations

from typing import Any

from docutils import nodes
from docutils.parsers.rst.directives.body import Sidebar

from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.transforms.post_transforms import SphinxPostTransform

SIDENOTE_OPTION = "book_use_sidenotes"

#: 行内边注的容器标签，供 CSS 与测试共用
SIDENOTE_CLASSES = ("sidenote", "marginnote")
#: 窄屏隐藏副本的标记类
DUPLICATE_CLASS = "d-n"
#: margin note 的正文前缀
MARGIN_MARKER = "{-}"


def _findall(node: nodes.Node, cls: type) -> list[nodes.Node]:
    """docutils 0.18+ 用 ``findall``；更老的版本只有 ``traverse``。"""
    findall = getattr(node, "findall", None)
    if findall is not None:
        return list(findall(cls))
    return list(node.traverse(cls))  # pragma: no cover - 旧 docutils 兜底


def _anchor(node: nodes.Element) -> str:
    names = node.get("names") or node.get("ids") or []
    return str(names[0]) if names else "sidenote-role-unknown"


def visit_sidenote_node(translator: Any, node: nodes.Element) -> None:
    """把行内边注渲染成「标签 + 复选开关」的无脚本结构。"""
    anchor = _anchor(node)
    if anchor.startswith("marginnote-"):
        translator.body.append(f'<label for="{anchor}" class="margin-toggle marginnote-label">')
    else:
        translator.body.append(f'<label for="{anchor}" class="margin-toggle">')
        translator.body.append(translator.starttag(node, "span"))


def depart_sidenote_node(translator: Any, node: nodes.Element) -> None:
    anchor = _anchor(node)
    if anchor.startswith("sidenote-"):
        translator.body.append("</span>\n\n")
    translator.body.append("</label>")
    translator.body.append(
        f'<input type="checkbox" id="{anchor}" name="{anchor}" class="margin-toggle">'
    )


class SideNoteNode(nodes.Element):
    """边注的引用端占位：只承载编号/符号，正文由同级 ``inline`` 承载。"""

    def __init__(self, rawsource: str = "", *children: nodes.Node, **attributes: Any) -> None:
        super().__init__("", *children, **attributes)

    @classmethod
    def register(cls, app: Sphinx) -> None:
        app.add_node(
            cls,
            override=True,
            html=(visit_sidenote_node, depart_sidenote_node),
        )


class Margin(Sidebar):
    """把块级内容放进右侧留白；可带一个标题参数。"""

    optional_arguments = 1
    required_arguments = 0

    def run(self) -> list[nodes.Node]:
        has_title = bool(self.arguments and self.arguments[0].strip())
        if not self.arguments:
            self.arguments = [""]
        produced = super().run()
        if not produced:  # pragma: no cover - Sidebar 至少产出一个节点
            return produced
        sidebar = produced[0]
        sidebar["classes"].append("margin")
        if not has_title and sidebar.children:
            first = sidebar.children[0]
            if isinstance(first, nodes.title) and not first.astext().strip():
                sidebar.children.pop(0)
        return produced


class FootnoteToSidenote(SphinxPostTransform):
    """把脚注引用就地换成边注；正文以 ``{-}`` 开头时转为无编号 margin note。"""

    default_priority = 1
    formats = ("html",)

    def run(self, **kwargs: Any) -> None:
        from .options import config_flag  # 延迟导入，避免循环依赖

        # 不用 self.app（Sphinx 11 前弃用）
        if not config_flag(self.config, SIDENOTE_OPTION):
            return

        footnotes = _findall(self.document, nodes.footnote)
        consumed: set[nodes.Node] = set()

        for ref in _findall(self.document, nodes.footnote_reference):
            footnote = self._match(ref, footnotes)
            if footnote is None:
                continue
            if self._convert(ref, footnote):
                consumed.add(footnote)

        for footnote in consumed:
            parent = footnote.parent
            if parent is not None:
                parent.remove(footnote)

    def _match(self, ref: nodes.Element, footnotes: list[nodes.Node]) -> nodes.Node | None:
        refid = ref.get("refid")
        ref_ids = list(ref.get("ids") or [])
        for footnote in footnotes:
            ids = list(footnote.get("ids") or [])
            if refid is not None and refid in ids:
                return footnote
            backrefs = list(footnote.get("backrefs") or [])
            if backrefs and ref_ids and backrefs[0] == ref_ids[0]:
                return footnote
        return None

    def _convert(self, ref: nodes.Element, footnote: nodes.Node) -> bool:
        if len(footnote.children) < 2:
            return False
        label = footnote.children[0].astext()
        body = list(footnote.children[1].children) if footnote.children[1].children else []
        if not body:
            return False

        is_margin = _starts_with_margin_marker(body[0])
        if is_margin:
            body[0] = _strip_margin_marker(body[0])

        content = nodes.inline()
        content["classes"].append("marginnote" if is_margin else "sidenote")
        if is_margin:
            content.extend(body)
        else:
            content.extend([nodes.superscript("", label), *body])

        anchor_class = "marginnote-role" if is_margin else "sidenote-role"
        marker = SideNoteNode()
        marker["names"].append(f"{anchor_class}-{label}")
        if not is_margin:
            marker.append(nodes.superscript("", label))

        duplicate = content.deepcopy()

        container = self._duplicate_before_container(ref, content)
        if container is not None:
            # 容器内只留窄屏副本；宽屏正文提到容器外
            duplicate["classes"].append(DUPLICATE_CLASS)
            container.replace_self([content, container])

        ref.replace_self([marker, duplicate])
        return True

    def _duplicate_before_container(self, ref: nodes.Element, content: nodes.Node) -> nodes.Node | None:
        """引用在提示框/表格里时，把边注正文提到容器之前（宽屏可见）。"""
        parent = ref.parent
        while parent is not None and not isinstance(parent, (nodes.section, addnodes.document)):
            if not isinstance(parent, (nodes.paragraph, nodes.footnote)):
                return parent
            parent = parent.parent
        return None


def _starts_with_margin_marker(node: nodes.Node) -> bool:
    return isinstance(node, nodes.Text) and node.astext().startswith(MARGIN_MARKER)


def _strip_margin_marker(node: nodes.Text) -> nodes.Node:
    text = node.astext()[len(MARGIN_MARKER) :]
    if not text.strip():
        return nodes.Text("")
    return nodes.Text(text)


def setup(app: Sphinx) -> None:
    """注册边注相关的节点、指令与变换。"""
    SideNoteNode.register(app)
    app.add_directive("margin", Margin)
    app.add_post_transform(FootnoteToSidenote)

"""Sphinx 文档构建 Invoke 任务包（双模式：builder-mode + ``-M`` 目标）。

按职责原子化为四个子模块，对外统一以 ``mystx.tasks.doc`` 暴露：

    _core.py        Sphinx 域底层（并行策略、选项合并、路径解析、-M 包装）
    builder.py     builder-mode 5 个根任务（build/clean/browse/tree/doctest）
    targets.py     ``-M`` 目标 3 个任务（target/linkcheck/help），以 ``doc`` 子 Collection 暴露
    _namespace.py  本域装配（``build_ns``）

下游用法：``from mystx.tasks import doc_ns``（域内实现名仍为 ``build_ns``），
或直接访问 ``mystx.tasks.doc.build`` / ``mystx.tasks.doc.build_targets_collection``。
"""
from ._namespace import build_ns
from .builder import browse, build, clean, doctest, tree
from .targets import build_targets_collection

__all__ = [
    "build_ns",
    "build",
    "clean",
    "browse",
    "tree",
    "doctest",
    "build_targets_collection",
]

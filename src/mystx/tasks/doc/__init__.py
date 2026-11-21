"""Sphinx 文档构建 Invoke 任务包（双模式：builder-mode + make-mode）。

按职责原子化为三个子模块，对外仍以 ``mystx.tasks.doc`` 统一暴露：

    _core.py       并行策略与公共底层（选项拆分、路径解析、命令执行）
    builder.py     builder-mode 5 个根任务（build/clean/browse/tree/doctest）
    make.py        make-mode 5 个任务与 ``make`` 子 Collection

下游用法不变：``from mystx.tasks import create_ns``，或直接访问
``mystx.tasks.doc.build`` / ``mystx.tasks.doc.build_make_collection``。
"""
from .builder import browse, build, clean, doctest, tree
from .make import build_make_collection

__all__ = [
    "build",
    "clean",
    "browse",
    "tree",
    "doctest",
    "build_make_collection",
]
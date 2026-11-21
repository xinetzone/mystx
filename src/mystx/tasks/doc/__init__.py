"""Sphinx 文档构建 Invoke 任务包（双模式：builder-mode + make-mode）。

按职责原子化为四个子模块，对外统一以 ``mystx.tasks.doc`` 暴露：

    _core.py       并行策略与公共底层（选项拆分、路径解析、命令执行）
    builder.py     builder-mode 5 个根任务（build/clean/browse/tree/doctest）
    make.py        make-mode 5 个任务与 ``make`` 子 Collection
    _namespace.py  命名空间装配（``create_ns``）

下游用法：``from mystx.tasks.doc import create_ns``（``mystx.tasks`` 仅作再导出门面），
或直接访问 ``mystx.tasks.doc.build`` / ``mystx.tasks.doc.build_make_collection``。
"""
from ._namespace import create_ns
from .builder import browse, build, clean, doctest, tree
from .make import build_make_collection

__all__ = [
    "create_ns",
    "build",
    "clean",
    "browse",
    "tree",
    "doctest",
    "build_make_collection",
]

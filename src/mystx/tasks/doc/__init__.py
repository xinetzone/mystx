"""Sphinx 文档构建 Invoke 任务包（builder-mode + ``-M`` 目标）。

按职责原子化为三个子模块，对外统一以 ``mystx.tasks.doc`` 暴露；
任务全部挂在 ``doc`` 子命名空间（``invoke doc.<name>``）：

    _core.py        Sphinx 域底层（并行策略、选项合并、路径解析、-M 包装）
    builder.py     本域 8 个任务（builder-mode 5 个 + ``-M`` 目标 3 个）
    _namespace.py  本域装配（``build_ns``）

下游用法：``from mystx.tasks import doc_ns``（域内实现名仍为 ``build_ns``），
或直接访问 ``mystx.tasks.doc.build`` 等任务函数。
"""
from ._namespace import build_ns
from .builder import browse, build, clean, doctest, tree

__all__ = ["build_ns", "build", "clean", "browse", "tree", "doctest"]

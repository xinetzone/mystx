"""mystx.tasks —— 任务包门面，具体实现位于 ``mystx.tasks.doc``。

本模块只保留 ``create_ns`` 与 ``doc`` 两个再导出，任务清单与用法说明见
``mystx.tasks.doc`` 及各任务自身的 docstring::

    from mystx.tasks import create_ns

    ns = create_ns(source="doc", target="_build/html", builddir="_build")
"""

from . import doc
from .doc import create_ns

__all__ = ["create_ns", "doc"]

"""mystx.tasks —— 任务包门面，实现位于 ``mystx.tasks.doc``。

``create_ns`` 与 ``doc`` 在此再导出，保持既有调用方式不变::

    from mystx.tasks import create_ns

    ns = create_ns(source="doc", target="_build/html", builddir="_build")

Builder-mode（根命名空间，默认）：
    invoke build         构建 HTML（增量）；可选 --clean/--browse/--nitpick
    invoke clean         删除构建目录
    invoke browse        本地 HTTP 预览
    invoke tree          文本树列构建产物
    invoke doctest       文档 doctest

Make-mode（子命名空间 ``make.``）：
    invoke make          默认任务：显示 Sphinx make-mode 帮助
    invoke make.html     构建 HTML
    invoke make.linkcheck  外链完整性校验
    invoke make.doctest    doctest（统一 builddir/doctest）
    invoke make.build target=latexpdf  通用包装 ``sphinx-build -M <target>``

新代码建议直接引用实现所在包：``from mystx.tasks.doc import create_ns``。
"""

from . import doc
from .doc import create_ns

__all__ = ["create_ns", "doc"]

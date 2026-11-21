"""Make-mode 文档任务（挂 ``make`` 子命名空间：``invoke make.<name>``）。

    make.build(target)  ——  ``sphinx-build -M <target>`` 通用包装
    make.html         ——  构建 HTML
    make.linkcheck    ——  外链完整性校验
    make.help          ——  显示 Sphinx make-mode 帮助
    make.doctest      ——  make-mode doctest
"""
from invoke import Collection, task

from ._core import _resolve_or, _run_make_mode


@task
def _make_build(
    _c,
    target: str,
    sourcedir: str = ".",
    builddir: str = "_build",
    opts: str = "",
) -> None:
    """``sphinx-build -M <target>`` 通用入口（make-mode build 别名）。"""
    src = _resolve_or(_c, "source", sourcedir, "doc")
    bd = _resolve_or(_c, "builddir", builddir, "_build")
    _run_make_mode(target, src, bd, opts=opts)


@task
def _make_html(
    _c,
    sourcedir: str = ".",
    builddir: str = "_build",
    opts: str = "",
) -> None:
    """make-mode：构建 HTML。"""
    src = _resolve_or(_c, "source", sourcedir, "doc")
    bd = _resolve_or(_c, "builddir", builddir, "_build")
    _run_make_mode("html", src, bd, opts)


@task
def _make_linkcheck(
    _c,
    sourcedir: str = ".",
    builddir: str = "_build",
    opts: str = "",
) -> None:
    """make-mode：检查所有外部链接完整性。"""
    src = _resolve_or(_c, "source", sourcedir, "doc")
    bd = _resolve_or(_c, "builddir", builddir, "_build")
    _run_make_mode("linkcheck", src, bd, opts)


@task(default=True)
def _make_help(
    _c,
    sourcedir: str = ".",
    builddir: str = "_build",
    opts: str = "",
) -> None:
    """make-mode：显示 Sphinx 帮助。"""
    src = _resolve_or(_c, "source", sourcedir, "doc")
    bd = _resolve_or(_c, "builddir", builddir, "_build")
    _run_make_mode("help", src, bd, opts)


@task
def _make_doctest(
    _c,
    sourcedir: str = ".",
    builddir: str = "_build",
    opts: str = "",
) -> None:
    """make-mode：运行 doctests（统一输出到 builddir/doctest）。"""
    src = _resolve_or(_c, "source", sourcedir, "doc")
    bd = _resolve_or(_c, "builddir", builddir, "_build")
    _run_make_mode("doctest", src, bd, opts)


def build_make_collection() -> Collection:
    """组装 make-mode 子 Collection（5 个任务）。"""
    ns = Collection("make")
    ns.add_task(_make_build, name="build")
    ns.add_task(_make_html, name="html")
    ns.add_task(_make_linkcheck, name="linkcheck")
    ns.add_task(_make_help, name="help", default=True)
    ns.add_task(_make_doctest, name="doctest")
    return ns

"""``-M`` 目标任务（Sphinx target 接口，挂 ``targets`` 子命名空间）。

    targets.build(target)  ——  ``sphinx-build -M <target>`` 通用包装
    targets.html           ——  构建 HTML
    targets.linkcheck      ——  外链完整性校验
    targets.help           ——  显示 Sphinx 内建目标帮助
    targets.doctest        ——  ``-M doctest``
"""
from invoke import Collection, task

from ._core import _resolve_or, _run_target


@task
def _target_build(
    _c,
    target: str,
    sourcedir: str = ".",
    builddir: str = "_build",
    opts: str = "",
) -> None:
    """``sphinx-build -M <target>`` 通用入口。"""
    src = _resolve_or(_c, "source", sourcedir, "doc")
    bd = _resolve_or(_c, "builddir", builddir, "_build")
    _run_target(target, src, bd, opts=opts)


@task
def _target_html(
    _c,
    sourcedir: str = ".",
    builddir: str = "_build",
    opts: str = "",
) -> None:
    """``-M html``：构建 HTML。"""
    src = _resolve_or(_c, "source", sourcedir, "doc")
    bd = _resolve_or(_c, "builddir", builddir, "_build")
    _run_target("html", src, bd, opts)


@task
def _target_linkcheck(
    _c,
    sourcedir: str = ".",
    builddir: str = "_build",
    opts: str = "",
) -> None:
    """``-M linkcheck``：检查所有外部链接完整性。"""
    src = _resolve_or(_c, "source", sourcedir, "doc")
    bd = _resolve_or(_c, "builddir", builddir, "_build")
    _run_target("linkcheck", src, bd, opts)


@task(default=True)
def _target_help(
    _c,
    sourcedir: str = ".",
    builddir: str = "_build",
    opts: str = "",
) -> None:
    """``-M help``：显示 Sphinx 内建目标帮助。"""
    src = _resolve_or(_c, "source", sourcedir, "doc")
    bd = _resolve_or(_c, "builddir", builddir, "_build")
    _run_target("help", src, bd, opts)


@task
def _target_doctest(
    _c,
    sourcedir: str = ".",
    builddir: str = "_build",
    opts: str = "",
) -> None:
    """``-M doctest``：运行 doctests（统一输出到 builddir/doctest）。"""
    src = _resolve_or(_c, "source", sourcedir, "doc")
    bd = _resolve_or(_c, "builddir", builddir, "_build")
    _run_target("doctest", src, bd, opts)


def build_targets_collection() -> Collection:
    """组装 ``-M`` 目标子 Collection（5 个任务）。"""
    ns = Collection("targets")
    ns.add_task(_target_build, name="build")
    ns.add_task(_target_html, name="html")
    ns.add_task(_target_linkcheck, name="linkcheck")
    ns.add_task(_target_help, name="help", default=True)
    ns.add_task(_target_doctest, name="doctest")
    return ns

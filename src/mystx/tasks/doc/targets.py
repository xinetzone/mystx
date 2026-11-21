"""``-M`` 目标任务（与 builder-mode 任务同挂 ``doc`` 子命名空间）。

只注册 builder-mode 没有的能力；与其等价的 ``html`` / ``doctest`` 不重复注册
（对应 ``invoke doc.build`` / ``invoke doc.doctest``）。

    doc.target <name>  ——  ``sphinx-build -M <target>`` 通用包装（latex/epub 等）
    doc.linkcheck      ——  外链完整性校验
    doc.help           ——  显示 Sphinx 内建目标帮助
"""
from invoke import task

from ._core import _resolve_or, _run_target


@task
def _target_target(
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


@task
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

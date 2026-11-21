"""``-M`` 目标任务（Sphinx target 接口，挂 ``doc`` 子命名空间）。

只注册根命名空间没有的能力；与根任务等价的 ``html`` / ``doctest`` 不重复注册
（对应 ``invoke build`` / ``invoke doctest``）。

    doc.target <name>  ——  ``sphinx-build -M <target>`` 通用包装（latex/epub 等）
    doc.linkcheck      ——  外链完整性校验
    doc.help           ——  显示 Sphinx 内建目标帮助
"""
from invoke import Collection, task

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


def build_targets_collection() -> Collection:
    """组装 ``-M`` 目标子 Collection（3 个任务，``help`` 为默认）。"""
    ns = Collection("doc")
    ns.add_task(_target_target, name="target")
    ns.add_task(_target_linkcheck, name="linkcheck")
    ns.add_task(_target_help, name="help", default=True)
    return ns

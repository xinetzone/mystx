"""Sphinx 文档任务（builder-mode 5 个 + ``-M`` 目标 3 个，挂 ``doc`` 子命名空间）。

builder-mode：``build``（默认）、``clean``、``browse``、``tree``、``doctest``；
``-M`` 目标：``target`` / ``linkcheck`` / ``help``。全部任务仅依赖标准库与
``invoke``，不调用第三方任务的私有实现。
"""
import os
import shutil
import sys
from pathlib import Path
from typing import Literal

from invoke import Exit, task

from .._shared import run_cmd
from ._core import (
    _PARALLEL_FLAG_DEFAULT,
    _builder_tokens,
    _resolve,
    _resolve_or,
    _run_target,
)
from ._serve import serve


@task(name="clean")
def clean(
    c,
    target: str | None = None,
    mode: Literal["builder", "targets"] = "builder",
    source: str | None = None,
    builddir: str | None = None,
    opts: str = "",
) -> None:
    """清理构建产物。``mode='builder'`` 只删单个 target 目录并回收空父目录；
    ``mode='targets'`` 等价于 ``sphinx-build -M clean``。"""
    if mode == "builder":
        tgt_path = Path(_resolve(c, "target", target, "_build/html")).resolve()
        buildroot = Path(_resolve(c, "builddir", builddir, "_build")).resolve()
        if not tgt_path.is_relative_to(buildroot):
            raise Exit(
                f"clean: 拒绝删除构建根之外的目录：{tgt_path}（构建根={buildroot}）"
            )
        if tgt_path.exists():
            shutil.rmtree(tgt_path)
        parent = tgt_path.parent
        while (
            parent != buildroot
            and parent.is_relative_to(buildroot)
            and parent.is_dir()
            and not any(parent.iterdir())
        ):
            parent.rmdir()
            parent = parent.parent
    elif mode == "targets":
        src = _resolve(c, "source", source, "doc")
        bd = _resolve(c, "builddir", builddir, "_build")
        _run_target("clean", sourcedir=src, builddir=bd, opts=opts)
    else:
        raise Exit(f"clean: unknown mode={mode!r} (expected 'builder' or 'targets')")


# 形参与任务同名，函数体经私有别名调用，避免 globals() 反射的隐式依赖
_clean_task = clean


@task
def browse(c, target: str | None = None, port: int = 8000) -> None:
    """启动本地 HTTP 服务器预览已构建的 HTML。"""
    target_path = Path(_resolve(c, "target", target, "_build/html"))
    if not target_path.exists():
        print(
            f"[browse] 构建目录不存在：{target_path}，请先运行 invoke doc.build",
            file=sys.stderr,
        )
        return
    serve(target_path, port)


@task
def tree(c, target: str | None = None) -> None:
    """以文本树形式列出 Sphinx 构建产物目录。"""
    target_path = Path(_resolve(c, "target", target, "_build/html"))
    if not target_path.exists():
        print(f"[tree] 构建目录不存在：{target_path}", file=sys.stderr)
        return
    for root, dirs, files in os.walk(target_path):
        dirs.sort()  # 顺序稳定；子目录由下一层递归打印，避免重复
        level = len(Path(root).relative_to(target_path).parts)
        indent = "│   " * level
        print(f"{indent}{os.path.basename(root)}/")
        sub = "│   " * (level + 1)
        for name in sorted(files):
            print(f"{sub}{name}")


@task
def doctest(
    c,
    source: str | None = None,
    build_dir: str | None = None,
    opts: str = "",
) -> None:
    """运行 Sphinx doctest 构建器（默认输出到 ``<builddir>/doctest``）。"""
    src = _resolve(c, "source", source, "doc")
    if build_dir is None:
        build_dir = os.path.join(_resolve(c, "builddir", None, "_build"), "doctest")
    run_cmd(c, _builder_tokens("-b doctest", src, build_dir, opts))


@task(default=True)
def build(
    c,
    clean: bool = False,
    browse: bool = False,
    nitpick: bool = False,
    opts: str | None = None,
    source: str | None = None,
    target: str | None = None,
) -> None:
    """构建 Sphinx 文档（builder-mode，默认 ``-b html``）。

    默认并行度按环境分流（见 ``_PARALLEL_FLAG_DEFAULT``）：CI 取 min(cpu, 8)，
    本地 POSIX 取 cpu-1，Windows 不加 ``-j``（Sphinx 依赖 fork）。
    显式传入 ``opts``（含空串）时完全尊重，不注入 ``-b html`` 与并行 flag。
    ``clean`` / ``browse`` 沿用本次解析出的 target。
    """
    if clean:
        _clean_task(c, target=target)
    src = _resolve(c, "source", source, "doc")
    tgt = _resolve(c, "target", target, "_build/html")
    if opts is None:
        opts = "-b html"
        if _PARALLEL_FLAG_DEFAULT:
            opts = f"{opts} {_PARALLEL_FLAG_DEFAULT}"
    extra = "-n -W -T" if nitpick else ""
    run_cmd(c, _builder_tokens(opts, src, tgt, extra))
    if browse:
        _browse_task(c, target=tgt)


_browse_task = browse


# ---------------------------------------------------------------------------
# ``-M`` 目标接口：builder-mode 未覆盖的能力（latex/epub 等），薄包装。
# ---------------------------------------------------------------------------


def _m_paths(c, sourcedir: str, builddir: str) -> tuple[str, str]:
    """``-M`` 任务的路径解析：占位默认值优先取配置，否则原样使用。"""
    return (
        _resolve_or(c, "source", sourcedir, "doc"),
        _resolve_or(c, "builddir", builddir, "_build"),
    )


@task
def _target_target(
    _c,
    target: str,
    sourcedir: str = ".",
    builddir: str = "_build",
    opts: str = "",
) -> None:
    """``sphinx-build -M <target>`` 通用入口。"""
    src, bd = _m_paths(_c, sourcedir, builddir)
    _run_target(target, src, bd, opts=opts)


@task
def _target_linkcheck(
    _c,
    sourcedir: str = ".",
    builddir: str = "_build",
    opts: str = "",
) -> None:
    """``-M linkcheck``：检查所有外部链接完整性。"""
    src, bd = _m_paths(_c, sourcedir, builddir)
    _run_target("linkcheck", src, bd, opts)


@task
def _target_help(
    _c,
    sourcedir: str = ".",
    builddir: str = "_build",
    opts: str = "",
) -> None:
    """``-M help``：显示 Sphinx 内建目标帮助。"""
    src, bd = _m_paths(_c, sourcedir, builddir)
    _run_target("help", src, bd, opts)

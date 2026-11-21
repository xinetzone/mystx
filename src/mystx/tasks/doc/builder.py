"""Builder-mode 文档任务（挂在根命名空间，``invoke <name>`` 直接调用）。

    build    (default)  ——  builder-mode 构建，支持 clean/browse/nitpick 链式开关
    clean              ——  删除单个 target 目录（mode='builder'）或 make-mode 全清理
    browse             ——  启动本地 HTTP 服务器预览
    tree               ——  文本树列出构建产物
    doctest            ——  builder-mode doctest

可选依赖：
    安装 ``invocations`` 后，browse/tree/doctest(builder) 复用其稳定实现；
    未安装时自动回退到 Python 标准库实现。
"""
import os
import shutil
import socket
import subprocess
import sys
import webbrowser
from pathlib import Path
from typing import Literal

from invoke import Exit, task

from ._core import (
    _PARALLEL_FLAG_DEFAULT,
    _collect_sphinx_opts,
    _resolve,
    _run_cmd,
    _run_make_mode,
)

try:
    from invocations import docs as _inv_docs  # type: ignore[import-not-found]
    _HAVE_INVOCATIONS = True
except ImportError:  # pragma: no cover - invocations 为可选依赖
    _inv_docs = None  # type: ignore[assignment]
    _HAVE_INVOCATIONS = False


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
    """构建 Sphinx 文档（builder-mode：默认 ``-b html`` + 按环境分流并行度）。

    并行策略（``_PARALLEL_FLAG_DEFAULT``）：
      - CI (``GITHUB_ACTIONS=1``) → ``-j min(cpu_count, 8)`` 稳定优先，防 IPC 爆炸
      - 本地 POSIX (非 win32)   → ``-j max(1, cpu_count-1)``  留 1 核给桌面
      - 本地 Windows           → 不加 ``-j``（Sphinx 依赖 POSIX fork，天然串行）

    便利开关：``clean`` 构建前清理；``browse`` 完成后自动打开预览；``nitpick`` 附加 ``-n -W -T`` 把警告当错误。
    调用者显式传入 ``opts``（非 None）时完全尊重，不自动注入并行 flag。
    """
    if clean:
        globals()["clean"](c, target=target)
    src = _resolve(c, "source", source, "docs")
    tgt = _resolve(c, "target", target, "_build/html")
    if opts is None:
        # 默认：builder=html + 环境分流的并行 flag
        opts = "-b html"
        if _PARALLEL_FLAG_DEFAULT:
            opts = f"{opts} {_PARALLEL_FLAG_DEFAULT}"
    extra: list[str] = ["-n", "-W", "-T"] if nitpick else []
    rebuilt = ["sphinx-build", *_collect_sphinx_opts(opts), *extra, src, tgt]
    _run_cmd(c, rebuilt)
    if browse:
        globals()["browse"](c, target=tgt)


@task(name="clean")
def clean(
    c,
    target: str | None = None,
    mode: Literal["builder", "make"] = "builder",
    source: str | None = None,
    builddir: str | None = None,
    opts: str = "",
) -> None:
    """清理构建产物。``mode='builder'``（默认）只删单个 target 目录并回收空父目录；
    ``mode='make'`` 等价 ``sphinx-build -M clean``（清理 builddir 下所有子构建）。"""
    if mode == "builder":
        tgt = _resolve(c, "target", target, "_build/html")
        if _HAVE_INVOCATIONS:
            _inv_docs._clean(c)  # type: ignore[union-attr]
        else:
            tgt_path = Path(tgt)
            if tgt_path.exists():
                shutil.rmtree(tgt_path)
        parent = os.path.dirname(tgt)
        while parent and os.path.isdir(parent) and not os.listdir(parent):
            os.rmdir(parent)
            parent = os.path.dirname(parent)
    elif mode == "make":
        src = _resolve(c, "source", source, "docs")
        bd = _resolve(c, "builddir", builddir, "_build")
        _run_make_mode("clean", sourcedir=src, builddir=bd, opts=opts)
    else:
        raise Exit(f"clean: unknown mode={mode!r} (expected 'builder' or 'make')")


@task
def browse(c, target: str | None = None, port: int = 8000) -> None:
    """启动本地 HTTP 服务器预览已构建的 HTML。"""
    tgt = _resolve(c, "target", target, "_build/html")
    if _HAVE_INVOCATIONS:
        _inv_docs._browse(c)  # type: ignore[union-attr]
        return
    target_path = Path(tgt)
    if not target_path.exists():
        print(f"[browse] 构建目录不存在：{target_path}，请先运行 invoke build", file=sys.stderr)
        return
    host = "127.0.0.1"
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex((host, port)) != 0:
                break
            port += 1
    url = f"http://{host}:{port}/"
    print(f"[browse] 启动 HTTP 服务器：{url}  (目录={target_path})；Ctrl+C 退出")
    webbrowser.open(url)
    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", host],
        cwd=str(target_path),
    )
    try:
        server.wait()
    except KeyboardInterrupt:
        server.terminate()


@task
def tree(c, target: str | None = None) -> None:
    """以文本树形式列出 Sphinx 构建产物目录。"""
    tgt = _resolve(c, "target", target, "_build/html")
    if _HAVE_INVOCATIONS:
        _inv_docs.tree(c)  # type: ignore[union-attr]
        return
    target_path = Path(tgt)
    if not target_path.exists():
        print(f"[tree] 构建目录不存在：{target_path}", file=sys.stderr)
        return
    for root, dirs, files in os.walk(target_path):
        level = len(Path(root).relative_to(target_path).parts)
        indent = "│   " * level
        print(f"{indent}{os.path.basename(root)}/")
        sub = "│   " * (level + 1)
        for name in sorted(dirs):
            print(f"{sub}{name}/")
        for name in sorted(files):
            print(f"{sub}{name}")


@task
def doctest(
    c,
    source: str | None = None,
    build_dir: str = "_build/doctest",
    opts: str = "",
) -> None:
    """运行 Sphinx doctest 构建器（builder-mode，独立 build_dir）。"""
    if _HAVE_INVOCATIONS:
        _inv_docs.doctest(c)  # type: ignore[union-attr]
        return
    src = _resolve(c, "source", source, "docs")
    tokens = ["sphinx-build", "-b", "doctest", *_collect_sphinx_opts(opts), src, build_dir]
    _run_cmd(c, tokens)
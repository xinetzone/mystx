"""Builder-mode 文档任务（挂在根命名空间，``invoke <name>`` 直接调用）。

    build    (default)  ——  builder-mode 构建，支持 clean/browse/nitpick 链式开关
    clean              ——  删除单个 target 目录（mode='builder'）或 make-mode 全清理
    browse             ——  启动本地 HTTP 服务器预览
    tree               ——  文本树列出构建产物
    doctest            ——  builder-mode doctest

全部任务仅依赖标准库与 ``invoke``，不调用第三方任务的私有实现，
避免可选依赖缺失或升级时的行为分叉。
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

from .._shared import run_cmd
from ._core import (
    _PARALLEL_FLAG_DEFAULT,
    _collect_sphinx_opts,
    _resolve,
    _run_make_mode,
)


@task(name="clean")
def clean(
    c,
    target: str | None = None,
    mode: Literal["builder", "make"] = "builder",
    source: str | None = None,
    builddir: str | None = None,
    opts: str = "",
) -> None:
    """清理构建产物。``mode='builder'`` 为默认值，只删单个 target 目录并回收空父目录；
    ``mode='make'`` 等价于 ``sphinx-build -M clean``，清理 builddir 下所有子构建。"""
    if mode == "builder":
        tgt = _resolve(c, "target", target, "_build/html")
        tgt_path = Path(tgt)
        if tgt_path.exists():
            shutil.rmtree(tgt_path)
        parent = os.path.dirname(tgt)
        while parent and os.path.isdir(parent) and not os.listdir(parent):
            os.rmdir(parent)
            parent = os.path.dirname(parent)
    elif mode == "make":
        src = _resolve(c, "source", source, "doc")
        bd = _resolve(c, "builddir", builddir, "_build")
        _run_make_mode("clean", sourcedir=src, builddir=bd, opts=opts)
    else:
        raise Exit(f"clean: unknown mode={mode!r} (expected 'builder' or 'make')")


# build 的 ``--clean``/``--browse`` 形参与任务同名，函数体经私有别名调用，
# 避免 ``globals()`` 反射带来的隐式依赖。
_clean_task = clean


@task
def browse(c, target: str | None = None, port: int = 8000) -> None:
    """启动本地 HTTP 服务器预览已构建的 HTML。"""
    tgt = _resolve(c, "target", target, "_build/html")
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


_browse_task = browse


@task
def tree(c, target: str | None = None) -> None:
    """以文本树形式列出 Sphinx 构建产物目录。"""
    tgt = _resolve(c, "target", target, "_build/html")
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
    src = _resolve(c, "source", source, "doc")
    tokens = ["sphinx-build", "-b", "doctest", *_collect_sphinx_opts(opts), src, build_dir]
    run_cmd(c, tokens)


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
      - 本地 Windows           → 不加 ``-j``，因 Sphinx 依赖 POSIX fork，天然串行

    便利开关：``clean`` 构建前清理；``browse`` 完成后自动打开预览；``nitpick`` 附加 ``-n -W -T`` 把警告当错误。
    两者都沿用本次解析出的 target，不会回到配置默认值。
    调用者显式传入 ``opts`` 且其值非 None 时完全尊重，不自动注入并行 flag。
    """
    if clean:
        _clean_task(c, target=target)
    src = _resolve(c, "source", source, "doc")
    tgt = _resolve(c, "target", target, "_build/html")
    if opts is None:
        # 默认：builder=html + 环境分流的并行 flag
        opts = "-b html"
        if _PARALLEL_FLAG_DEFAULT:
            opts = f"{opts} {_PARALLEL_FLAG_DEFAULT}"
    extra: list[str] = ["-n", "-W", "-T"] if nitpick else []
    rebuilt = ["sphinx-build", *_collect_sphinx_opts(opts), *extra, src, tgt]
    run_cmd(c, rebuilt)
    if browse:
        _browse_task(c, target=tgt)
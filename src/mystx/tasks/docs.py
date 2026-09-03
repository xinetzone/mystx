"""Sphinx 文档构建 Invoke 任务（双模式：builder-mode + make-mode）。

**任务组织：

**Builder-mode（根命名空间，默认语义，下游 `create_ns 直接挂根）：
    build    (default)  ——  builder-mode 构建，支持 clean/browse/nitpick 链式开关
    clean              ——  删除单个 target 目录（mode='builder'）或 make-mode 全清理
    browse             ——  启动本地 HTTP 服务器预览
    tree               ——  文本树列出构建产物
    doctest            ——  builder-mode doctest

**Make-mode（挂 ``make`` 子命名空间：``invoke make.<name>``）：
    make.build(target)  ——  ``sphinx-build -M <target>`` 通用包装
    make.html         ——  构建 HTML
    make.linkcheck    ——  外链完整性校验
    make.help          ——  显示 Sphinx make-mode 帮助
    make.doctest      ——  make-mode doctest

可选依赖：
    安装 ``invocations`` 后，browse/tree/doctest(builder) 复用其稳定实现；
    未安装时自动回退到 Python 标准库实现。
"""
import os
import shlex
import shutil
import socket
import subprocess
import sys
import webbrowser
from pathlib import Path
from typing import Literal

from invoke import Collection, Exit, task

try:
    from invocations import docs as _inv_docs  # type: ignore[import-not-found]
    _HAVE_INVOCATIONS = True
except ImportError:  # pragma: no cover - invocations 为可选依赖
    _inv_docs = None  # type: ignore[assignment]
    _HAVE_INVOCATIONS = False


# ---------------------------------------------------------------------------
# 公共底层：env 合并 + shlex 拆分 + 执行
# ---------------------------------------------------------------------------

def _split_cli_args(value: str) -> list[str]:
    """按 shell 风格拆分字符串；Windows 禁用 POSIX 语义。"""
    if not value.strip():
        return []
    return shlex.split(value, posix=os.name != "nt")


def _collect_sphinx_opts(opts: str = "") -> list[str]:
    """合并三层选项优先级：``$SPHINXOPTS`` → ``$O`` → 传入 ``opts``。"""
    args: list[str] = []
    for part in (os.environ.get("SPHINXOPTS", ""), os.environ.get("O", ""), opts):
        args.extend(_split_cli_args(part))
    return args


def _join_shell(tokens: list[str]) -> str:
    """把已拆分的 token 列表重新 shlex.quote 后拼成一条安全 shell 字符串。"""
    return " ".join(shlex.quote(t) for t in tokens if t != "")


def _resolve(c, key: str, override: str | None, default: str | None = None) -> str:
    """解析优先级：显式参数 > 配置字典 > 默认值。"""
    if override is not None:
        return override
    cfg = c.config.get("sphinx", {})
    return cfg.get(key, default)


def _resolve_or(c, key: str, override: str, fallback: str) -> str:
    """当 override 是外部约定默认占位符（``'.'`` / ``'_build'``）时，优先查配置；否则直接用 override。"""
    cfg = c.config.get("sphinx", {})
    if override in (".", "_build"):
        return cfg.get(key) or fallback
    return override


def _run_cmd(c, cmd_tokens: list[str]) -> None:
    """POSIX 默认 pty=True、Windows pty=False；可通过 ``run.pty`` 显式覆盖。"""
    pty = c.config.get("run", {}).get("pty", os.name != "nt")
    c.run(_join_shell(cmd_tokens), pty=pty)


def _run_make_mode(
    target: str,
    sourcedir: str,
    builddir: str,
    opts: str = "",
) -> None:
    """包装 ``sphinx-build -M`` 模式；读取 ``$SPHINXBUILD`` 覆盖可执行路径。"""
    sphinx_build = os.environ.get("SPHINXBUILD", "sphinx-build")
    command = [
        sphinx_build,
        "-M",
        target,
        sourcedir,
        builddir,
        *_collect_sphinx_opts(opts),
    ]
    try:
        completed = subprocess.run(command, check=False)
    except FileNotFoundError as exc:
        raise Exit(
            "The 'sphinx-build' command was not found. Set SPHINXBUILD to the "
            "full path of the executable or add it to PATH."
        ) from exc
    if completed.returncode != 0:
        raise Exit(code=completed.returncode)


# ---------------------------------------------------------------------------
# Builder-mode（根命名空间，默认挂载）
# ---------------------------------------------------------------------------

@task(default=True)
def build(
    c,
    clean: bool = False,
    browse: bool = False,
    nitpick: bool = False,
    opts: str = "-b html -j auto",
    source: str | None = None,
    target: str | None = None,
) -> None:
    """构建 Sphinx 文档（builder-mode：默认 ``-b html -j auto`` 增量构建）。

    便利开关：``clean`` 构建前清理；``browse`` 完成后自动打开预览；``nitpick`` 附加 ``-n -W -T`` 把警告当错误。
    """
    if clean:
        globals()["clean"](c)
    src = _resolve(c, "source", source, "docs")
    tgt = _resolve(c, "target", target, "_build/html")
    if opts is None:
        opts = ""
    extra: list[str] = ["-n", "-W", "-T"] if nitpick else []
    rebuilt = ["sphinx-build", *_collect_sphinx_opts(opts), *extra, src, tgt]
    _run_cmd(c, rebuilt)
    if browse:
        globals()["browse"](c)


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
    ``mode='make'`` 等价 ``sphinx-build -M clean（清理 builddir 下所有子构建。"""
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


# ---------------------------------------------------------------------------
# Make-mode（子命名空间 make.xxx；通过 ``invoke make.html`` 调用）
# ---------------------------------------------------------------------------

@task
def _make_build(
    _c,
    target: str,
    sourcedir: str = ".",
    builddir: str = "_build",
    opts: str = "",
) -> None:
    """``sphinx-build -M <target>`` 通用入口（make-mode build 别名）。"""
    src = _resolve_or(_c, "source", sourcedir, "docs")
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
    src = _resolve_or(_c, "source", sourcedir, "docs")
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
    src = _resolve_or(_c, "source", sourcedir, "docs")
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
    src = _resolve_or(_c, "source", sourcedir, "docs")
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
    src = _resolve_or(_c, "source", sourcedir, "docs")
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

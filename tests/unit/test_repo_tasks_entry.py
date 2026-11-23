"""仓库根 ``tasks.py`` 入口与 pages.yml 调用契约的防回归守护。

背景：invoke 仅能从执行目录的 ``tasks`` 集合发现任务。2026-08 重构删除
仓库根 tasks.py 后，``.github/workflows/pages.yml`` 仍执行 ``invoke doc``，
CI 在构建步骤以 ``Can't find any collection named 'tasks'!`` 秒级失败
（run 35072625311, 2026-09-16）。本测试静态对账三件事：

1. 仓库根 tasks.py 存在且可加载；
2. 命名空间把源目录/产物目录锁定为仓库的 ``doc/`` 布局；
3. pages.yml 中每个 ``invoke <task>`` 调用名都能在命名空间中解析。
"""
import importlib.util
import re
import shlex
import sys
from pathlib import Path

import pytest

pytest.importorskip("invoke")

from invoke import Collection, Context, Exit  # noqa: E402

_REPO_ROOT = Path(__file__).resolve().parents[2]
_TASKS_PY = _REPO_ROOT / "tasks.py"
_PAGES_YML = _REPO_ROOT / ".github" / "workflows" / "pages.yml"
_INVOKE_CALL = re.compile(r"\binvoke\s+([A-Za-z_][\w.]*)")


def _load_root_namespace() -> Collection:
    """以文件路径方式加载仓库根 tasks.py 并返回其 ``ns``。"""
    assert _TASKS_PY.is_file(), (
        f"仓库根任务入口缺失：{_TASKS_PY}；invoke 将无法发现任务集合，"
        "参见 CI run 35072625311（Can't find any collection named 'tasks'!）"
    )
    spec = importlib.util.spec_from_file_location("mystx_repo_root_tasks", _TASKS_PY)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(spec.name, None)
    ns = getattr(module, "ns", None)
    assert isinstance(ns, Collection), "根 tasks.py 必须暴露 invoke.Collection 实例 ns"
    return ns


def test_root_tasks_py_locks_doc_layout():
    """根命名空间的 sphinx 路径配置必须是锚定仓库 doc/ 布局的绝对路径。

    绝对化由 doc 域自动完成：cmd.exe 不支持 UNC 工作目录（会退到 C:\\Windows，
    相对路径 ``doc`` 被解析到 ``C:\\Windows\\doc``），故任务不得依赖 cwd。
    """
    ns = _load_root_namespace()
    sphinx_cfg = ns.configuration()["sphinx"]
    assert sphinx_cfg == {
        "source": str(_REPO_ROOT / "doc"),
        "target": str(_REPO_ROOT / "doc" / "_build" / "html"),
        "target_file": "index.html",
        "builddir": str(_REPO_ROOT / "doc" / "_build"),
    }


def test_root_namespace_exposes_everything_under_doc():
    """所有任务必须以 ``doc.`` 前缀暴露，根命名空间不再散落任务。"""
    ns = _load_root_namespace()
    assert not ns.tasks, f"根命名空间不应直接挂任务，实际存在 {sorted(ns.tasks)}"
    assert ns.default == "doc", "根默认入口必须是 doc 子集合"
    doc = ns.collections["doc"]
    assert doc.default == "build"
    for name in ("build", "clean", "browse", "tree", "doctest",
                 "target", "linkcheck", "help"):
        assert name in doc.tasks, f"doc 子命名空间缺少任务 {name!r}"
    # html 与 build 功能重复，不得再注册
    assert "html" not in doc.tasks, "doc 子命名空间不应重复注册 html"


def _resolve_task(ns: Collection, name: str):
    if "." in name:
        head, _, tail = name.partition(".")
        return ns.collections[head].tasks.get(tail)
    return ns.tasks.get(name)


def test_pages_workflow_invoke_calls_are_registered():
    """pages.yml 里的每个 invoke <task> 必须在根命名空间可解析。"""
    ns = _load_root_namespace()
    workflow = _PAGES_YML.read_text(encoding="utf-8")
    called = set(_INVOKE_CALL.findall(workflow))
    assert called, "pages.yml 中未发现 invoke 调用，工作流构建步骤可能已改型"
    for name in sorted(called):
        assert _resolve_task(ns, name) is not None, (
            f"pages.yml 调用了未注册的 invoke 任务 {name!r}；"
            f"可用根任务：{sorted(ns.tasks)}，子命名空间：{sorted(ns.collections)}"
        )


def test_build_task_command_targets_doc_tree(monkeypatch):
    """build 任务拼装的 sphinx-build 命令必须指向 doc → doc/_build/html。"""
    from mystx.tasks import doc

    ns = _load_root_namespace()
    monkeypatch.setattr(doc.builder, "_PARALLEL_FLAG_DEFAULT", "-j 4")
    captured: list[str] = []
    ctx = Context(config=ns.configuration())
    monkeypatch.setattr(ctx, "run", lambda cmd, pty: captured.append(cmd))

    doc.builder.build(ctx)

    assert len(captured) == 1
    tokens = shlex.split(captured[0], posix=False)
    assert tokens[0] == "sphinx-build"
    assert "-b" in tokens and tokens[tokens.index("-b") + 1] == "html"
    assert tokens[-2:] == [
        str(_REPO_ROOT / "doc"),
        str(_REPO_ROOT / "doc" / "_build" / "html"),
    ]
    assert "-j" in tokens and tokens[tokens.index("-j") + 1] == "4"


def test_doc_ns_owned_by_doc_package():
    """``doc_ns`` 实现归属 ``mystx.tasks.doc.build_ns``，门面仅再导出同一对象。"""
    from mystx.tasks import doc, doc_ns

    assert doc_ns is doc.build_ns, "mystx.tasks.doc_ns 必须是 mystx.tasks.doc.build_ns"
    assert doc_ns().configuration()["sphinx"]["source"] == str(_REPO_ROOT / "doc")


def test_build_chain_flags_propagate_effective_target(monkeypatch):
    """``build --clean --browse --target X`` 的链式开关必须沿用本次解析出的 target。"""
    from mystx.tasks import doc

    ns = _load_root_namespace()
    monkeypatch.setattr(doc.builder, "_PARALLEL_FLAG_DEFAULT", "")
    ctx = Context(config=ns.configuration())
    monkeypatch.setattr(ctx, "run", lambda cmd, pty: None)
    seen: dict[str, str | None] = {}
    monkeypatch.setattr(doc.builder, "_clean_task", lambda _c, target=None: seen.setdefault("clean", target))
    monkeypatch.setattr(doc.builder, "_browse_task", lambda _c, target=None: seen.setdefault("browse", target))

    doc.builder.build(ctx, clean=True, browse=True, target="out/html")

    assert seen["clean"] == "out/html", "build --clean 未把 target 传给 clean，会误删默认目录"
    assert seen["browse"] == "out/html", "build --browse 未把 target 传给 browse，会打开默认目录"


def test_sphinxbuild_env_is_shared_by_all_entries(monkeypatch):
    """AC-5：``SPHINXBUILD`` 必须同时作用于 build / doctest / ``-M`` 目标三个入口。"""
    from mystx.tasks import doc
    from mystx.tasks.doc import _core

    fake = "/opt/fake/sphinx-build"
    monkeypatch.setenv("SPHINXBUILD", fake)
    monkeypatch.setattr(doc.builder, "_PARALLEL_FLAG_DEFAULT", "")

    ns = _load_root_namespace()
    ctx = Context(config=ns.configuration())
    captured: list[str] = []
    monkeypatch.setattr(ctx, "run", lambda cmd, pty: captured.append(cmd))

    doc.builder.build(ctx)
    doc.builder.doctest(ctx)

    assert len(captured) == 2
    for cmd in captured:
        assert shlex.split(cmd, posix=False)[0] == fake

    seen: list[list[str]] = []

    class _Done:
        returncode = 0

    monkeypatch.setattr(
        _core.subprocess, "run", lambda command, check: seen.append(command) or _Done()
    )
    _core._run_target("clean", "doc", "_build")

    assert seen and seen[0][0] == fake, "-M 目标入口未复用 SPHINXBUILD 解析"


def test_clean_refuses_target_outside_buildroot(tmp_path):
    """AC-4：target 指向构建根之外时必须拒绝删除，且不误删任何目录。"""
    from mystx.tasks import doc

    buildroot = tmp_path / "build"
    outside = tmp_path / "outside" / "html"
    buildroot.mkdir()
    outside.mkdir(parents=True)
    marker = outside / "index.html"
    marker.write_text("keep", encoding="utf-8")

    ctx = Context(config={"sphinx": {"builddir": str(buildroot)}})

    with pytest.raises(Exit):
        doc.builder.clean(ctx, target=str(outside))

    assert marker.is_file(), "越界 target 不应删除任何目录"


def test_clean_removes_inside_target_without_touching_buildroot(tmp_path):
    """AC-4：构建根内的 target 正常删除，但构建根本身保留。"""
    from mystx.tasks import doc

    buildroot = tmp_path / "build"
    target = buildroot / "html"
    target.mkdir(parents=True)
    (target / "index.html").write_text("x", encoding="utf-8")

    ctx = Context(config={"sphinx": {"builddir": str(buildroot)}})

    doc.builder.clean(ctx, target=str(target))

    assert not target.exists()
    assert buildroot.is_dir()


def test_clean_removes_empty_parents_within_buildroot(tmp_path):
    """AC-4：空父目录可回收，但不得越过构建根。"""
    from mystx.tasks import doc

    buildroot = tmp_path / "build"
    target = buildroot / "a" / "html"
    target.mkdir(parents=True)
    (target / "index.html").write_text("x", encoding="utf-8")

    doc.builder.clean(
        Context(config={"sphinx": {"builddir": str(buildroot)}}), target=str(target)
    )

    assert not target.exists()
    assert not (buildroot / "a").exists(), "空父目录应被回收"
    assert buildroot.is_dir(), "回收不得越过构建根"


def test_tree_prints_each_directory_once(tmp_path, capsys):
    """AC-9：``tree`` 每个目录只打印一行，且按字典序输出文件。"""
    from mystx.tasks import doc

    root = tmp_path / "html"
    (root / "a" / "b").mkdir(parents=True)
    (root / "index.html").write_text("x", encoding="utf-8")
    (root / "z.txt").write_text("x", encoding="utf-8")
    (root / "a" / "one.txt").write_text("x", encoding="utf-8")
    (root / "a" / "b" / "two.txt").write_text("x", encoding="utf-8")

    doc.builder.tree(Context(config={"sphinx": {}}), target=str(root))

    assert capsys.readouterr().out.splitlines() == [
        "html/",
        "│   index.html",
        "│   z.txt",
        "│   a/",
        "│   │   one.txt",
        "│   │   b/",
        "│   │   │   two.txt",
    ]


def test_tree_reports_missing_dir(tmp_path, capsys):
    from mystx.tasks import doc

    doc.builder.tree(Context(config={"sphinx": {}}), target=str(tmp_path / "nope"))

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "构建目录不存在" in captured.err


def test_browse_reports_missing_dir_without_starting_server(tmp_path, capsys):
    from mystx.tasks import doc

    doc.builder.browse(Context(config={"sphinx": {}}), target=str(tmp_path / "nope"))

    assert "构建目录不存在" in capsys.readouterr().err


def test_clean_targets_mode_delegates_to_m(monkeypatch):
    from mystx.tasks import doc

    seen: dict = {}
    monkeypatch.setattr(doc.builder, "_run_target", lambda *a, **k: seen.update(args=a, kwargs=k))
    ctx = Context(config={"sphinx": {"source": "doc", "builddir": "_build"}})

    doc.builder.clean(ctx, mode="targets", opts="-q")

    assert seen["args"] == ("clean",)
    assert seen["kwargs"] == {"sourcedir": "doc", "builddir": "_build", "opts": "-q"}


def test_clean_rejects_unknown_mode():
    from mystx.tasks import doc

    with pytest.raises(Exit):
        doc.builder.clean(Context(config={"sphinx": {}}), mode="bogus")


def test_target_wrappers_delegate_to_m_builder(monkeypatch):
    from mystx.tasks import doc

    calls: list[tuple] = []
    monkeypatch.setattr(doc.builder, "_run_target", lambda *a, **k: calls.append((a, k)))
    ctx = Context(config={"sphinx": {"source": "doc", "builddir": "_build"}})

    doc.builder._target_target(ctx, "latex")
    doc.builder._target_linkcheck(ctx)
    doc.builder._target_help(ctx)

    assert [c[0][0] for c in calls] == ["latex", "linkcheck", "help"]
    assert calls[0][0] == ("latex", "doc", "_build")
    assert calls[0][1] == {"opts": ""}
    assert calls[1][0] == ("linkcheck", "doc", "_build", "")
    assert calls[2][0] == ("help", "doc", "_build", "")


def test_build_nitpick_and_explicit_opts_skip_parallel(monkeypatch):
    """显式传入 opts（含空串）时完全尊重，不自动注入 ``-b html`` 与并行 flag。"""
    from mystx.tasks import doc

    monkeypatch.delenv("SPHINXOPTS", raising=False)
    monkeypatch.delenv("O", raising=False)
    captured: list[str] = []
    ctx = Context(
        config={"sphinx": {"source": "doc", "target": "_build/html", "builddir": "_build"}}
    )
    monkeypatch.setattr(ctx, "run", lambda cmd, pty: captured.append(cmd))

    doc.builder.build(ctx, nitpick=True, opts="")

    tokens = shlex.split(captured[0], posix=False)
    assert tokens[1:4] == ["-n", "-W", "-T"]
    assert tokens[-2:] == ["doc", "_build/html"]
    assert "-b" not in tokens and "-j" not in tokens


def test_doctest_uses_explicit_build_dir(monkeypatch):
    from mystx.tasks import doc

    monkeypatch.delenv("SPHINXOPTS", raising=False)
    monkeypatch.delenv("O", raising=False)
    captured: list[str] = []
    ctx = Context(config={"sphinx": {"source": "doc", "builddir": "_build"}})
    monkeypatch.setattr(ctx, "run", lambda cmd, pty: captured.append(cmd))

    doc.builder.doctest(ctx, build_dir="out/doctest")

    tokens = shlex.split(captured[0], posix=False)
    assert tokens[1:3] == ["-b", "doctest"]
    assert tokens[-2:] == ["doc", "out/doctest"]


def test_browse_serves_built_html_end_to_end(tmp_path, capsys, monkeypatch):
    """集成：真实拉起 ``http.server``，浏览器回调取到页面即证明目录与端口正确。"""
    import socket
    import subprocess
    import sys
    import time
    import urllib.request

    from mystx.tasks import doc

    html = tmp_path / "html"
    html.mkdir()
    (html / "index.html").write_text("<h1>MYSTX_BROWSE_OK</h1>", encoding="utf-8")

    probe = socket.socket()
    probe.bind(("127.0.0.1", 0))
    free_port = probe.getsockname()[1]
    probe.close()

    real_popen = subprocess.Popen
    started: list = []

    def _popen(*args, **kwargs):
        proc = real_popen(*args, **kwargs)
        started.append((proc, args, kwargs))
        return proc

    bodies: dict[str, str] = {}

    def _open(url):
        deadline = time.monotonic() + 10
        while True:
            try:
                with urllib.request.urlopen(url, timeout=1) as resp:
                    bodies[url] = resp.read().decode("utf-8")
                break
            except OSError:
                if time.monotonic() > deadline:
                    raise
                time.sleep(0.05)
        started[0][0].terminate()

    monkeypatch.setattr(subprocess, "Popen", _popen)
    monkeypatch.setattr(doc.builder.webbrowser, "open", _open)

    try:
        doc.builder.browse(
            Context(config={"sphinx": {}}), target=str(html), port=free_port
        )
    finally:
        for proc, _, _ in started:
            if proc.poll() is None:
                proc.terminate()
                proc.wait(timeout=5)

    url = f"http://127.0.0.1:{free_port}/"
    assert "MYSTX_BROWSE_OK" in bodies.get(url, "")
    _, args, kwargs = started[0]
    assert args[0] == [
        sys.executable,
        "-m",
        "http.server",
        str(free_port),
        "--bind",
        "127.0.0.1",
    ]
    assert kwargs["cwd"] == str(html)
    assert url in capsys.readouterr().out


def test_browse_skips_occupied_port(tmp_path, monkeypatch):
    import socket

    from mystx.tasks import doc

    html = tmp_path / "html"
    html.mkdir()
    (html / "index.html").write_text("x", encoding="utf-8")

    blocker = socket.socket()
    blocker.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    blocker.bind(("127.0.0.1", 0))
    blocker.listen(1)
    busy_port = blocker.getsockname()[1]

    class _Server:
        def wait(self):
            return 0

    opened: list[str] = []
    monkeypatch.setattr(doc.builder.subprocess, "Popen", lambda *a, **k: _Server())
    monkeypatch.setattr(doc.builder.webbrowser, "open", opened.append)

    try:
        doc.builder.browse(
            Context(config={"sphinx": {}}), target=str(html), port=busy_port
        )
    finally:
        blocker.close()

    chosen = int(opened[0].rsplit(":", 1)[1].rstrip("/"))
    assert chosen > busy_port

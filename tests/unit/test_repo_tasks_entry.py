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

from invoke import Collection, Context  # noqa: E402

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

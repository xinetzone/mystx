"""文档任务命名空间的装配逻辑（``build_ns``）。

把全部 doc 任务收进单个名为 ``doc`` 的子 Collection，使其统一以 ``doc.<name>``
暴露（``invoke doc.build`` 等）；该子 Collection 同时是根命名空间的默认入口，
Sphinx 路径默认值写入 ``sphinx`` 配置段后由子任务继承。

域契约：本函数只装配 ``doc`` 域，根命名空间由调用方（仓库 ``tasks.py``）决定。
"""
from invoke import Collection

from .builder import (
    _target_help,
    _target_linkcheck,
    _target_target,
    browse,
    build,
    clean,
    doctest,
    tree,
)

__all__ = ["build_ns"]


def build_ns(
    *,
    source: str = "doc",
    target: str = "_build/html",
    target_file: str = "index.html",
    builddir: str = "_build",
) -> Collection:
    """组装 ``doc`` 域命名空间，注入 Sphinx 路径默认配置。

    所有参数关键字-only，避免调用者混淆参数顺序。

    Args:
        source:      Sphinx 源目录（含 conf.py）。默认 ``"doc"``。
        target:      Builder-mode HTML 输出目录。默认 ``"_build/html"``。
        target_file: 首页文件相对路径（预留 browse / CI 用）。默认 ``"index.html"``。
        builddir:    ``-M`` 目标总构建目录（所有 target 挂其下）。默认 ``"_build"``。

    Returns:
        根 Collection，其唯一子集合 ``doc`` 含 8 个任务（builder-mode 5 个 +
        ``-M`` 目标 3 个），并被设为根默认入口。
    """
    doc = Collection("doc")
    doc.add_task(build, default=True)
    doc.add_task(clean)
    doc.add_task(browse)
    doc.add_task(tree)
    doc.add_task(doctest)
    doc.add_task(_target_target, name="target")
    doc.add_task(_target_linkcheck, name="linkcheck")
    doc.add_task(_target_help, name="help")

    ns = Collection()
    ns.add_collection(doc, default=True)
    ns.configure(
        {
            "sphinx": {
                "source": source,
                "target": target,
                "target_file": target_file,
                "builddir": builddir,
            }
        }
    )
    return ns

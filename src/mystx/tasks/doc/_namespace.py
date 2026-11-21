"""文档任务命名空间的装配逻辑（``build_ns``）。

把 builder-mode 的 5 个根任务与 make-mode 子 Collection 装配成单个
``invoke.Collection``，并把 Sphinx 路径默认值写入 ``sphinx`` 配置段。

域契约：本函数只装配 ``doc`` 域，不触碰根命名空间。
"""
from invoke import Collection

from .builder import browse, build, clean, doctest, tree
from .make import build_make_collection

__all__ = ["build_ns"]


def build_ns(
    *,
    source: str = "doc",
    target: str = "_build/html",
    target_file: str = "index.html",
    builddir: str = "_build",
) -> Collection:
    """组装 ``doc`` 域的 Invoke Collection，注入 Sphinx 路径默认配置。

    所有参数关键字-only，避免调用者混淆参数顺序。

    Args:
        source:      Sphinx 源目录（含 conf.py）。默认 ``"doc"``。
        target:      Builder-mode HTML 输出目录。默认 ``"_build/html"``。
        target_file: 首页文件相对路径（预留 browse / CI 用）。默认 ``"index.html"``。
        builddir:    Make-mode 总构建目录（所有 ``-M`` 目标挂其下）。默认 ``"_build"``。

    Returns:
        挂好 builder-mode 5 个根任务 + make-mode 子 Collection 的 invoke.Collection。
    """
    ns = Collection()
    ns.add_task(build, default=True)
    ns.add_task(clean)
    ns.add_task(browse)
    ns.add_task(tree)
    ns.add_task(doctest)
    ns.add_collection(build_make_collection())
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

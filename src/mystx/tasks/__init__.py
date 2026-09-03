"""mystx.tasks —— 可复用的 Sphinx + Invoke 任务命名空间（双模式：builder + make）。

典型用法（项目根 ``tasks.py``）::

    from mystx.tasks import create_ns

    ns = create_ns(source="docs", target="_build/html", builddir="_build")

Builder-mode（根命名空间，默认）：
    invoke build         构建 HTML（增量）；可选 --clean/--browse/--nitpick
    invoke clean         删除构建目录
    invoke browse        本地 HTTP 预览
    invoke tree          文本树列构建产物
    invoke doctest       文档 doctest

Make-mode（子命名空间 ``make.``）：
    invoke make          默认任务：显示 Sphinx make-mode 帮助
    invoke make.html     构建 HTML
    invoke make.linkcheck  外链完整性校验
    invoke make.doctest    doctest（统一 builddir/doctest）
    invoke make.build target=latexpdf  通用包装 ``sphinx-build -M <target>``
"""

from invoke import Collection

from . import docs

__all__ = ["create_ns", "docs"]


def create_ns(
    *,
    source: str = "docs",
    target: str = "_build/html",
    target_file: str = "index.html",
    builddir: str = "_build",
) -> Collection:
    """组装一个 Invoke Collection，注入 Sphinx 路径默认配置。

    所有参数关键字-only，避免调用者混淆参数顺序。

    Args:
        source:      Sphinx 源目录（含 conf.py）。默认 ``"docs"``。
        target:      Builder-mode HTML 输出目录。默认 ``"_build/html"``。
        target_file: 首页文件相对路径（预留 browse / CI 用）。默认 ``"index.html"``。
        builddir:    Make-mode 总构建目录（所有 ``-M`` 目标挂其下）。默认 ``"_build"``。

    Returns:
        挂好 builder-mode 5 个根任务 + make-mode 子 Collection 的 invoke.Collection。
    """
    ns = Collection()
    ns.add_task(docs.build, default=True)
    ns.add_task(docs.clean)
    ns.add_task(docs.browse)
    ns.add_task(docs.tree)
    ns.add_task(docs.doctest)
    ns.add_collection(docs.build_make_collection())
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

"""文档任务命名空间的装配逻辑（``build_ns``）。

把全部 doc 任务收进单个名为 ``doc`` 的子 Collection，使其统一以 ``doc.<name>``
暴露（``invoke doc.build`` 等）；该子 Collection 同时是根命名空间的默认入口，
Sphinx 路径默认值写入 ``sphinx`` 配置段后由子任务继承。

路径策略：``source`` / ``target`` / ``builddir`` 在装配时统一转为**绝对路径**，
锚点为向上查找到的含 ``<source>/conf.py`` 的项目根（找不到则退回当前工作目录）。
这样任务不依赖 cwd——cmd.exe 无法把 UNC 路径设为工作目录（会退到 ``C:\\Windows``），
相对路径会解析到错误位置；绝对化后任意启动方式都能正确定位文档源。

域契约：本函数只装配 ``doc`` 域，根命名空间由调用方（仓库 ``tasks.py``）决定。
"""
from pathlib import Path

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


def _anchor_root(source: str) -> Path:
    """定位项目根：从本包所在目录向上找含 ``<source>/conf.py`` 的目录。"""
    for parent in Path(__file__).resolve().parents:
        if (parent / source / "conf.py").is_file():
            return parent
    return Path.cwd()


def _under(base: Path, path: str) -> str:
    """相对路径拼到 ``base`` 下并绝对化；已是绝对路径则原样返回。"""
    p = Path(path)
    return str(p if p.is_absolute() else base / p)


def build_ns(
    *,
    source: str = "doc",
    target: str = "_build/html",
    target_file: str = "index.html",
    builddir: str | None = None,
    root: str | Path | None = None,
) -> Collection:
    """组装 ``doc`` 域命名空间，注入 Sphinx 路径默认配置（绝对路径）。

    所有参数关键字-only，避免调用者混淆参数顺序。

    Args:
        source:      Sphinx 源目录（含 conf.py），相对 ``root``。默认 ``"doc"``。
        target:      Builder-mode HTML 输出目录，相对 ``source``。默认 ``"_build/html"``。
        target_file: 首页文件相对路径（预留 browse / CI 用）。默认 ``"index.html"``。
        builddir:    ``-M`` 目标总构建目录，相对 ``root``；默认 ``<source>/_build``。
        root:        项目根；默认向上查找含 ``<source>/conf.py`` 的目录。

    Returns:
        根 Collection，其唯一子集合 ``doc`` 含 8 个任务（builder-mode 5 个 +
        ``-M`` 目标 3 个），并被设为根默认入口。
    """
    base = Path(root).expanduser().resolve() if root is not None else _anchor_root(source)
    src = _under(base, source)
    tgt = _under(Path(src), target)
    bd = _under(base, builddir) if builddir is not None else str(Path(src) / "_build")

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
                "source": src,
                "target": tgt,
                "target_file": target_file,
                "builddir": bd,
            }
        }
    )
    return ns

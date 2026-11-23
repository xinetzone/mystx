"""Sphinx ``setup()``：文档指令注册与并行守卫。"""
from sphinx.application import Sphinx

from mystx.myst_docs import register_docs_directives
from mystx.parallel import connect_parallel_guard

from .meta import release

# 上游未声明 parallel_{read,write}_safe 的扩展会被 Sphinx 判为串行；
# 需要并行时在此表补充扩展名（守卫实现见 mystx.parallel）。
PARALLEL_SAFE_OVERRIDES: dict[str, tuple[bool, bool]] = {}


def setup(app: Sphinx):
    """注册文档指令与并行守卫，并声明本扩展并行安全。"""
    register_docs_directives(app)
    connect_parallel_guard(app, PARALLEL_SAFE_OVERRIDES)
    return {
        "version": release,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }

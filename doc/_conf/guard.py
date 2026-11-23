"""Sphinx ``setup()``：文档指令注册与并行守卫。"""
from sphinx.application import Sphinx

from mystx.myst_docs import register_docs_directives
from mystx.parallel import connect_parallel_guard

from .meta import release

# P1-A 审计结论：新增第三方扩展时，如果其上游 setup() 未显式声明
# parallel_{read,write}_safe=True，Sphinx 会将其视为 None 并退化为串行。
# 覆写表与 fail-fast 守卫的实现见 mystx.parallel：表内补充扩展名即可
# 启用并行，不再需要逐个去上游提 PR；守卫仅在显式要求并行时生效。
# 审计参考: docs/retrospective/reports/documentation-governance/
#           sphinx-parallel-build-5k-scale-20260903/index.md
PARALLEL_SAFE_OVERRIDES: dict[str, tuple[bool, bool]] = {
    # "autoapi.extension": (True, True),      # 需要时取消注释
    # "mystx.ext.gallery": (True, True),      # 需要时取消注释
}


def setup(app: Sphinx):
    """Add functions to the Sphinx setup."""
    # MyST 文档工具指令（myst-config / myst-example 等）由包内统一注册：
    # 示例指令的 CSS 类名沿用 local.css 依赖的 myst-example* 契约。
    register_docs_directives(app)

    # 覆写表与 fail-fast 守卫见 PARALLEL_SAFE_OVERRIDES 上方说明。
    connect_parallel_guard(app, PARALLEL_SAFE_OVERRIDES)

    return {
        "version": release,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }

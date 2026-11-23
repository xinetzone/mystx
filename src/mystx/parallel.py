"""并行构建安全：中心化覆写表 + fail-fast 守卫。

Sphinx 只承认扩展 ``setup()`` 返回的 ``parallel_read_safe`` /
``parallel_write_safe``；未声明的第三方扩展按 ``None`` 处理，``-j N`` 会
**静默退化为串行**，只在 ``-v`` 日志里留下逐条告警。

本模块把该场景收拢为两个可复用原语，供任意 Sphinx 项目复用：

* :func:`apply_parallel_safe_overrides`：按扩展名批量声明并行安全，
  不必逐个去上游提 PR；
* :func:`connect_parallel_guard`：在 ``env-before-read-docs`` 上挂
  fail-fast 断言——调用方**显式**要求并行（``-j`` / ``$SPHINX_BUILD_JOBS``）
  而仍有扩展阻塞时立即报错，并列出阻塞扩展名；纯串行构建不受打扰。
"""

from collections.abc import Mapping

from sphinx.application import Sphinx
from sphinx.util import logging

logger = logging.getLogger(__name__)

#: 覆写表的形状：``{扩展名: (parallel_read_safe, parallel_write_safe)}``。
ParallelSafeOverrides = Mapping[str, tuple[bool, bool]]

#: 守卫挂载的默认事件。其契约签名为 ``(app, env, docnames)``。
GUARD_EVENT = "env-before-read-docs"


def find_parallel_blockers(app: Sphinx) -> list[str]:
    """列出已加载、但未显式声明 read 并行安全的扩展名（按加载顺序）。"""
    blockers: list[str] = []
    for name, ext in app.extensions.items():
        if getattr(ext, "parallel_read_safe", None) is not True:
            blockers.append(name)
    return blockers


def apply_parallel_safe_overrides(
    app: Sphinx,
    overrides: ParallelSafeOverrides,
) -> list[str]:
    """按覆写表为已加载扩展设置并行安全标记。

    未加载的扩展名会被跳过（而非报错）：同一份覆写表可以跨项目复用，
    而各项目实际装配的扩展集合并不相同。

    Returns:
        实际被覆写的扩展名列表，便于调用方记录或断言。
    """
    applied: list[str] = []
    for name, (read_safe, write_safe) in overrides.items():
        ext = app.extensions.get(name)
        if ext is None:
            logger.debug("并行覆写跳过未加载的扩展：%s", name)
            continue
        setattr(ext, "parallel_read_safe", bool(read_safe))
        setattr(ext, "parallel_write_safe", bool(write_safe))
        applied.append(name)
    return applied


def assert_parallel_ready(
    app: Sphinx,
    env: object | None = None,
    docnames: object | None = None,
) -> None:
    """``env-before-read-docs`` 钩子：并行被阻塞时立即失败。

    仅在调用方确实要求并行（``app.parallel > 0``）时生效，避免纯串行
    构建被打扰。``env`` / ``docnames`` 本钩子不使用，但必须在签名中接收，
    以满足事件契约。
    """
    if app.parallel <= 0 or app.is_parallel_allowed("read"):
        return
    blockers = find_parallel_blockers(app)
    detail = f"阻塞扩展：{blockers}" if blockers else "未发现阻塞扩展，请以 -v 查看逐扩展告警"
    raise RuntimeError(
        "并行读取已被禁用，但构建显式要求并行。"
        f"{detail}。可在覆写表中声明 parallel_read_safe=True，"
        "或移除这些扩展后重试。"
    )


def connect_parallel_guard(
    app: Sphinx,
    overrides: ParallelSafeOverrides | None = None,
    *,
    event: str = GUARD_EVENT,
) -> list[str]:
    """先应用覆写表，再挂上 fail-fast 守卫。

    Returns:
        实际被覆写的扩展名列表（无覆写时为空列表）。
    """
    applied = apply_parallel_safe_overrides(app, overrides or {})
    app.connect(event, assert_parallel_ready)
    return applied

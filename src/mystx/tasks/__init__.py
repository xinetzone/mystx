"""mystx.tasks —— 任务包门面，按"域"组织，具体实现位于各域子包。

当前域：``doc``（Sphinx 文档构建）。新增域须遵守四条契约：

1. 域自包含：``tasks/<domain>/`` 提供 ``build_ns(**opt) -> Collection``，
   只装配本域任务，不触碰根命名空间。
2. 域之间不得互相 import；通用执行原语只能来自 ``tasks/_shared.py``。
3. 每个域写自己的配置段（如 ``sphinx``），不在根级散键。
4. 根级任务名是稀缺资源：第二域落地时须显式声明并做重名断言
   （invoke 的 ``add_task`` 对同名任务是静默覆盖）。

用法::

    from mystx.tasks import build_ns

    ns = build_ns(source="doc", target="_build/html", builddir="_build")
"""

from .doc import build_ns

__all__ = ["build_ns"]

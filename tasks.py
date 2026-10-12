"""mystx 仓库级 invoke 任务入口（CI 与本地文档构建共用）。

invoke 只能从执行目录的 ``tasks`` 集合发现任务，本文件是 ``mystx.tasks``
任务包的薄适配层，把源目录与产物目录锁定为仓库的 ``doc/`` 布局：

    invoke build            构建 HTML 到 doc/_build/html（默认任务）
    invoke clean            清理构建产物
    invoke browse           本地 HTTP 预览
    invoke make.linkcheck   外链完整性校验

``.github/workflows/pages.yml`` 的调用名由
``tests/unit/test_repo_tasks_entry.py`` 与本命名空间静态对账，
防止工作流命令与任务注册再次失配（见 CI run 35072625311）。
"""
from mystx.tasks import create_ns

ns = create_ns(source="doc", target="doc/_build/html", builddir="doc/_build")

"""mystx 仓库级 invoke 任务入口（CI 与本地文档构建共用）。

invoke 只能从执行目录的 ``tasks`` 集合发现任务，本文件是 ``mystx.tasks``
任务包的薄适配层，把源目录与产物目录锁定为仓库的 ``doc/`` 布局：

    invoke doc.build        构建 HTML 到 doc/_build/html（默认任务）
    invoke doc.clean        清理构建产物
    invoke doc.browse       本地 HTTP 预览
    invoke doc.linkcheck    外链完整性校验

``.github/workflows/pages.yml`` 的调用名由
``tests/unit/test_repo_tasks_entry.py`` 与本命名空间静态对账，
防止工作流命令与任务注册再次失配（见 CI run 35072625311）。
"""
from pathlib import Path

from mystx.tasks import doc_ns

# 路径锚定到本文件所在目录并绝对化：cmd.exe 不能把 UNC 路径设为工作目录，
# 会退到 C:\Windows，相对路径随之解析到错误位置（\\10.16.11.3 共享上必现）。
_ROOT = Path(__file__).resolve().parent

ns = doc_ns(
    source=str(_ROOT / "doc"),
    target=str(_ROOT / "doc" / "_build" / "html"),
    builddir=str(_ROOT / "doc" / "_build"),
)

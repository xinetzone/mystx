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
from mystx.tasks import doc_ns

# 路径锚定与绝对化由 doc 域自行完成（见 mystx.tasks.doc._namespace），
# 不必在此重复计算：cmd.exe 不支持 UNC 工作目录（会退到 C:\Windows），
# 相对路径会解析到错误位置（\\10.16.11.3 共享上必现）。
ns = doc_ns()

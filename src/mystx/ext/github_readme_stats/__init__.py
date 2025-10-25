"""
mystx.ext.github_stats — GitHub Readme Stats 指令入口

该子包提供三条指令，用于在 Sphinx 文档中嵌入 GitHub Readme Stats 卡片::
- `github-stats`：用户统计卡片；
- `github-top-langs`：常用语言占比卡片；
- `github-pinned-repo`：置顶仓库卡片。

此模块导出指令类，并提供 `setup(app)` 以便 Sphinx 自动注册。
注意：卡片由外部服务 `https://github-readme-stats.vercel.app/` 渲染，选项与主题取值以该服务为准。
"""

from .stats import GitHubStatsDirective
from .top_langs import GitHubTopLangsDirective
from .pinned_repo import GitHubPinnedRepoDirective


def setup(app):
    """注册三条 GitHub Stats 相关指令到 Sphinx。

    Args:
        app: Sphinx 应用实例。

    Returns:
        dict: 扩展元信息，包含版本号与并行读取安全性标识。
    """
    app.add_directive("github-stats", GitHubStatsDirective)
    app.add_directive("github-top-langs", GitHubTopLangsDirective)
    app.add_directive("github-pinned-repo", GitHubPinnedRepoDirective)
    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }

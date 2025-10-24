"""mystx.ext — 文档扩展包

该包提供在 reStructuredText / MyST 文档中嵌入 GitHub Readme Stats 卡片的指令实现。

子模块:
  - github_stats: 包含以下指令类，用于渲染不同类型的卡片:

    - GitHubStatsDirective: 展示用户基础统计。
    - GitHubTopLangsDirective: 展示编程语言占比。
    - GitHubPinnedRepoDirective: 展示置顶仓库信息。

    用法:
      作为 Sphinx 扩展使用时，需要在 ``setup()`` 中注册指令，例如::

        >>> from mystx.ext.github_stats.stats import GitHubStatsDirective
        >>> from mystx.ext.github_stats.top_langs import GitHubTopLangsDirective
        >>> from mystx.ext.github_stats.pinned_repo import GitHubPinnedRepoDirective
        >>> def setup(app):
        ...     app.add_directive("github-stats", GitHubStatsDirective)
        ...     app.add_directive("github-top-langs", GitHubTopLangsDirective)
        ...     app.add_directive("github-pinned-repo", GitHubPinnedRepoDirective)

    在文档中（.rst 或 MyST）即可直接使用上述指令插入卡片。

    .. note::

      - 这些指令依赖外部服务 ``https://github-readme-stats.vercel.app/``，渲染结果取决于该服务。
      - ``theme`` 等选项由该服务提供，值的可用性以其文档为准。
"""
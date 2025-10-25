"""GitHub 置顶仓库卡片指令。

提供 GitHubPinnedRepoDirective，将用户名与仓库名渲染为 GitHub Readme Stats 的 pin 卡片。

Example:

    .. code-block:: rst

       .. github-pinned-repo::
          :username: octocat
          :repo: hello-world
          :theme: dark
"""
from docutils import nodes
from docutils.parsers.rst import directives
from .base import BaseGitHubCardDirective

class GitHubPinnedRepoDirective(BaseGitHubCardDirective):
    """渲染 GitHub 置顶仓库卡片。

    选项:

    - username（必填）：GitHub 用户名；
    - repo（必填）：仓库名；
    - theme（可选）：主题名称，默认为 default。
    - link（可选）：点击卡片跳转的链接地址。

    示例参见模块文档的用法。
    """
    option_spec = {
        "username": directives.unchanged_required,
        "repo": directives.unchanged_required,
        "theme": directives.unchanged,
        "link": directives.uri,
    }

    def run(self):
        """根据指令选项构建卡片 URL 并返回 HTML 节点。

        Returns:
            list[nodes.Node]: 单元素列表，包含原始 HTML ``<img>`` 节点。
        """
        username = self.options.get("username")
        repo = self.options.get("repo")
        if not username or not repo:
            msg = (
                "github-pinned-repo: 需要提供 :username: 和 :repo: 选项"
            )
            return [
                self.state_machine.reporter.error(msg, line=self.lineno)
            ]

        opts = {
            "username": username,
            "repo": repo,
            "theme": self.options.get("theme", "default"),
        }
        url = self.build_url("https://github-readme-stats.vercel.app/api/pin", opts)
        link = self.options.get("link")
        if link:
            html = f'<a href="{link}"><img src="{url}" alt="Pinned Repo"></a>'
            return [nodes.raw('', html, format='html')]
        return [self.create_image_node(url, alt="Pinned Repo")]

"""
GitHub 最常用语言（Top Languages）卡片指令。

`GitHubTopLangsDirective` 使用 GitHub Readme Stats 服务生成语言占比卡片，
支持 `layout`、`theme` 与 `langs_count` 等选项。
"""
from .base import BaseGitHubCardDirective
from docutils.parsers.rst import directives

class GitHubTopLangsDirective(BaseGitHubCardDirective):
    """渲染 GitHub Top Languages 卡片。

    选项：
    - `username`（必填）：GitHub 用户名；
    - `layout`（可选）：布局样式，默认为 `compact`；
    - `theme`（可选）：主题名称，默认为 `default`；
    - `langs_count`（可选）：展示语言数量，默认为 `6`。

    示例（reStructuredText）：

    .. code-block:: rst

       .. github-top-langs::
          :username: octocat
          :layout: compact
          :theme: dark
          :langs_count: 8
    """
    option_spec = {
        "username": directives.unchanged_required,
        "layout": directives.unchanged,
        "theme": directives.unchanged,
        "langs_count": directives.positive_int,
    }

    def run(self):
        """根据选项构建 Top Languages 卡片 URL 并返回 HTML 节点。

        Returns:
            list[nodes.Node]: 单元素列表，包含原始 HTML `<img>` 节点。
        """
        opts = {
            "username": self.options["username"],
            "layout": self.options.get("layout", "compact"),
            "theme": self.options.get("theme", "default"),
            "langs_count": self.options.get("langs_count", 6),
        }
        url = self.build_url("https://github-readme-stats.vercel.app/api/top-langs", opts)
        return [self.create_image_node(url, alt="Top Languages")]

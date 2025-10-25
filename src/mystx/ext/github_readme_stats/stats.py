"""
GitHub 用户统计卡片指令。

`GitHubStatsDirective` 使用 GitHub Readme Stats 服务生成用户统计卡片，
支持选项 `theme`、`show_icons` 与 `hide` 控制外观与显示内容。
"""
from .base import BaseGitHubCardDirective
from docutils.parsers.rst import directives

class GitHubStatsDirective(BaseGitHubCardDirective):
    """渲染 GitHub 用户基础统计卡片。

    选项：
    - `username`（必填）：GitHub 用户名；
    - `theme`（可选）：主题名称，默认为 `default`；
    - `show_icons`（可选 flag）：出现该选项即开启图标显示；
    - `hide`（可选）：以逗号分隔的统计项列表，例如 `issues,contribs`。

    示例（reStructuredText）：

    .. code-block:: rst

       .. github-stats::
          :username: octocat
          :theme: dark
          :show_icons:
          :hide: issues,contribs
    """
    option_spec = {
        "username": directives.unchanged_required,
        "theme": directives.unchanged,
        "show_icons": directives.flag,
        "hide": directives.unchanged,
    }

    def run(self):
        """根据选项构建统计卡片 URL 并返回 HTML 节点。

        Returns:
            list[nodes.Node]: 单元素列表，包含原始 HTML `<img>` 节点。
        """
        opts = {
            "username": self.options["username"],
            "theme": self.options.get("theme", "default"),
            "show_icons": "show_icons" in self.options,
            "hide": self.options.get("hide", "")
        }
        url = self.build_url("https://github-readme-stats.vercel.app/api", opts)
        return [self.create_image_node(url, alt="GitHub Stats")]

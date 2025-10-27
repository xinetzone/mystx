"""WakaTime 统计卡片指令。

提供 ``GitHubWakaTimeDirective``，使用 GitHub Readme Stats 服务渲染 WakaTime 统计卡片。
参考上游用法：https://github-readme-stats.vercel.app/api/wakatime?username=willianrod

支持选项（与上游一致的常用项） :

- ``username`` （必填）：WakaTime 用户名；
- ``theme`` （可选）：主题名称，默认 ``default``；
- ``layout`` （可选）：布局样式（例如 ``compact``）；
- ``range`` （可选）：时间范围（如 ``last_7_days``、``last_30_days``、``last_6_months``、``last_year``、``all_time``）；
- ``api_domain`` （可选）：自定义 WakaTime API 域名（如 Hakatime/Wakapi）；
- ``custom_title`` （可选）：自定义标题；
- ``hide_title`` （可选 flag）：隐藏标题；
- ``hide_border`` （可选 flag）：隐藏边框。

示例:

.. code-block:: rst

    .. github-wakatime::
        :username: willianrod
        :layout: compact
        :theme: tokyonight
        :range: last_7_days

"""
from docutils.parsers.rst import directives
from .base import BaseGitHubCardDirective


class GitHubWakaTimeDirective(BaseGitHubCardDirective):
    """渲染 WakaTime 统计卡片。

    选项见模块文档说明。
    """
    option_spec = {
        "username": directives.unchanged_required,
        "theme": directives.unchanged,
        "layout": directives.unchanged,
        "range": directives.unchanged,
        "api_domain": directives.unchanged,
        "custom_title": directives.unchanged,
        "hide_title": directives.flag,
        "hide_border": directives.flag,
    }

    def run(self):
        """根据选项构建 WakaTime 卡片 URL 并返回 HTML 节点。"""
        opts = {
            "username": self.options["username"],
            "theme": self.options.get("theme", "default"),
        }
        # 可选参数按需附加
        if "layout" in self.options:
            opts["layout"] = self.options["layout"]
        if "range" in self.options:
            opts["range"] = self.options["range"]
        if "api_domain" in self.options:
            opts["api_domain"] = self.options["api_domain"]
        if "custom_title" in self.options:
            opts["custom_title"] = self.options["custom_title"]
        if "hide_title" in self.options:
            opts["hide_title"] = True
        if "hide_border" in self.options:
            opts["hide_border"] = True

        url = self.build_url("https://github-readme-stats.vercel.app/api/wakatime", opts)
        return [self.create_image_node(url, alt="WakaTime Stats")]
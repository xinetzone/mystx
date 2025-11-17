"""GitHub Readme Stats 指令的基础工具。

提供基类 ``BaseGitHubCardDirective``，封装:

- 将选项字典转换为查询字符串；
- 生成原始 HTML ``<img>`` 节点用于嵌入卡片。
"""
from urllib.parse import urlencode
from html import escape
from docutils import nodes
from docutils.parsers.rst import Directive

class BaseGitHubCardDirective(Directive):
    """GitHub 卡片指令的通用基类。

    继承自 ``docutils.parsers.rst.Directive``，为各具体指令提供
    URL 构建与 HTML 节点生成的通用能力。
    """
    has_content = False

    def build_url(self, base_url: str, options: dict) -> str:
        """根据基础地址和选项构建完整查询 URL。

        Args:
            base_url: GitHub Readme Stats 接口基础地址，例如
                ``https://github-readme-stats.vercel.app/api``。
            options: 指令选项字典；布尔值 True 会被序列化为
                ``key=true``，其他类型以 ``key=value`` 形式拼接。

        Returns:
            完整的查询 URL 字符串。
        """
        cleaned = {k: v for k, v in options.items() if v not in (None, "")}
        flags = {k: True for k, v in cleaned.items() if isinstance(v, bool) and v}
        scalars = {k: v for k, v in cleaned.items() if not isinstance(v, bool)}
        query = urlencode({**scalars, **flags})
        return f"{base_url}?{query}"

    def create_image_node(self, url: str, alt: str = "GitHub Card"):
        """创建原始 HTML 节点，以 ``<img>`` 标签插入卡片图片。

        Args:
            url: 图片地址（通常为 GitHub Readme Stats 服务的卡片 URL）。
            alt: 图片的替代文本。

        Returns:
            ``docutils.nodes.raw`` 节点，可直接嵌入到最终 HTML。
        """
        html = f'<img src="{escape(url)}" alt="{escape(alt)}">'
        return nodes.raw('', html, format='html')

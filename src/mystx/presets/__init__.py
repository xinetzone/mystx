"""mystx — Sphinx + MyST 文档构建可复用配置层预设包。

两套装配契约：

极简预设返回扁平字典，``setup`` 在字典内::

    from mystx.presets import build_minimal_myst_config
    globals().update(build_minimal_myst_config({"project": "notes", "author": "me"}))

完整站点返回 ``(values, setup)``，由 ``apply_site_config`` 单次注入::

    from mystx.presets import apply_site_config
    setup = apply_site_config(globals(), site_url="https://example.com/docs/")

预设定位：
  - build_minimal_myst_config（来自 presets.minimal_myst）：仅 myst_parser + 双 MyST 兼容钩子，适合个人轻量笔记
  - build_mystx_site_config（来自 presets.mystx_site）：完整文档站机制（扩展装配、默认值下放、主题回退），返回 (SiteConfig, setup)
  - apply_site_config（来自 presets.mystx_site）：把站点取值注入给定命名空间并交回 setup，conf.py 的唯一装配入口
  - configure_site_fonts（来自 presets.mystx_site）：字体注册副作用，由站点显式调用
  - presets.mystx_docs：本项目文档站的**具体画像**（身份、主题选项、外部链接），
    不从包门面导出，仅供 ``doc/conf.py`` 使用

注意：OKF 专属预设（okf_docs）属 Non-Goals 未迁移。
"""

from typing import TYPE_CHECKING

from .minimal_myst import build_config as build_minimal_myst_config
from .mystx_site import apply_config as apply_site_config
from .mystx_site import build_config as build_mystx_site_config
from .mystx_site import configure_site_fonts

if TYPE_CHECKING:
    # 仅供类型检查器从门面解析 ``SiteConfig``；运行时不在包门面创建第二个定义，
    # 否则 autoapi 会为同名类生成两个目标，触发 ref.python 歧义告警。
    from .mystx_site import SiteConfig as SiteConfig

__all__ = [
    "apply_site_config",
    "build_minimal_myst_config",
    "build_mystx_site_config",
    "configure_site_fonts",
]

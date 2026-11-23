"""mystx — Sphinx + MyST 文档构建可复用配置层预设包。

预设定位：
  - build_minimal_myst_config（来自 presets.minimal_myst）：仅 myst_parser + 双 MyST 兼容钩子，适合个人轻量笔记
  - build_mystx_site_config（来自 presets.mystx_site）：完整文档站机制（扩展装配、默认值下放、主题回退），返回 (SiteConfig, setup)
  - apply_site_config（来自 presets.mystx_site）：把站点取值注入给定命名空间并交回 setup，conf.py 的唯一装配入口
  - configure_site_fonts（来自 presets.mystx_site）：字体注册副作用，由站点显式调用

注意：OKF 专属预设（okf_docs）属 Non-Goals 未迁移。
"""

from .minimal_myst import build_config as build_minimal_myst_config
from .mystx_site import apply_config as apply_site_config
from .mystx_site import build_config as build_mystx_site_config
from .mystx_site import configure_site_fonts

__all__ = [
    "apply_site_config",
    "build_minimal_myst_config",
    "build_mystx_site_config",
    "configure_site_fonts",
]

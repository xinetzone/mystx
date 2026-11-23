"""mystx — Sphinx + MyST 文档构建可复用配置层预设包。

预设定位：
  - build_minimal_myst_config（来自 presets.minimal_myst）：仅 myst_parser + 双 MyST 兼容钩子，适合个人轻量笔记
  - build_mystx_site_config（来自 presets.mystx_site）：完整文档站机制（扩展装配、默认值下放、主题与字体、setup 钩子）

注意：OKF 专属预设（okf_docs）属 Non-Goals 未迁移。
"""

from .minimal_myst import build_config as build_minimal_myst_config
from .mystx_site import build_config as build_mystx_site_config

__all__ = ["build_minimal_myst_config", "build_mystx_site_config"]

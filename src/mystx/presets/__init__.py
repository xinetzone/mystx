"""mystx — Sphinx + MyST 文档构建可复用配置层预设包。

预设定位：
  - build_minimal_myst_config（来自 presets.minimal_myst）：仅 myst_parser + 双 MyST 兼容钩子，适合个人轻量笔记

注意：OKF 专属预设（okf_docs）属 Non-Goals 未迁移。
"""

from .minimal_myst import build_config as build_minimal_myst_config

__all__ = ["build_minimal_myst_config"]

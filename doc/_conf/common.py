"""``doc/_conf`` 共享路径与可选依赖探测。"""
from pathlib import Path

from mystx.utils import has_module

# doc/_conf/common.py → doc/_conf → doc → 项目根
ROOT = Path(__file__).resolve().parents[2]

__all__ = ["ROOT", "has_module"]

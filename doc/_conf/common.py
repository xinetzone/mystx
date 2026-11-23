"""``doc/_conf`` 分组共享的路径常量与可选依赖探测。

本模块是所有分组的依赖起点：``ROOT`` 指向 mystx 项目根，``has_module``
统一封装可选扩展的可用性判断，避免各分组各写一份 ``find_spec``。
"""
from __future__ import annotations

import importlib.util as _ilut
from pathlib import Path

# doc/_conf/common.py → doc/_conf → doc → 项目根
ROOT = Path(__file__).resolve().parents[2]
DOC_DIR = ROOT / "doc"


def has_module(mod: str) -> bool:
    """判断模块是否可导入（Sphinx 可选扩展的装配前置）。"""
    return _ilut.find_spec(mod) is not None

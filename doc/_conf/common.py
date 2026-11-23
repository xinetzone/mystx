"""``doc/_conf`` 分组共享的路径常量与可选依赖探测。

本模块是所有分组的依赖起点：``ROOT`` 指向 mystx 项目根；``has_module``
直接再导出包内实现，不在文档目录另留一份 ``find_spec`` 副本。
"""
from pathlib import Path

from mystx.utils import has_module

# doc/_conf/common.py → doc/_conf → doc → 项目根
ROOT = Path(__file__).resolve().parents[2]
DOC_DIR = ROOT / "doc"

__all__ = ["DOC_DIR", "ROOT", "has_module"]

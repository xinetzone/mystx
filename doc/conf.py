#!/usr/bin/env python3
"""Sphinx 文档配置入口。

站点取值与装配顺序整体在 ``mystx.presets.mystx_docs``；本文件只负责定位仓库
根目录并把画像注入本模块命名空间。
"""
import sys
from pathlib import Path

from mystx.presets.mystx_docs import configure

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "doc"))

setup = configure(globals(), root=ROOT)

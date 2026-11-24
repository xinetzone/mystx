#!/usr/bin/env python3
"""Sphinx 文档配置入口。

本文件自己持有站点身份，并负责定位仓库根目录、把画像分两段交给 Sphinx；其余
取值与装配顺序在 ``mystx.presets.mystx_docs``。

Sphinx 的契约是「conf.py 的模块命名空间即配置」：``sphinx.config`` 先 ``exec``
本文件，再以该命名空间构造 ``Config``。但只有少数键必须在那个时刻就位——
``extensions`` 用于加载扩展，``language`` / ``locale_dirs`` / ``gettext_compact``
用于初始化 i18n，都发生在 ``config-inited`` 之前；``version`` / ``release``
一并显式给出，让侧栏与页脚元数据一眼可见。

其余键在 ``setup`` 注册的 ``config-inited`` 监听器里统一下发：该事件晚于扩展
加载、早于构建器创建与源文件扫描，核心校验（优先级 790-800）与各扩展的处理
都在其后，因此读到的是最终值。
"""

import sys
from pathlib import Path

from mystx.presets.mystx_docs import build_config

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "doc"))

_profile, _setup = build_config(root=ROOT)

# 站点身份：只有这一个站点，直接写在门面上，不经画像
project = "mystx"
author = "xinetzone"
copyright = "2026, xinetzone"

# 早读键：Sphinx 在 config-inited 之前就要用，必须在模块层可见
extensions = _profile["extensions"]
language = _profile["language"]
locale_dirs = _profile["locale_dirs"]
gettext_compact = _profile["gettext_compact"]
version = _profile["version"]
release = _profile["release"]

# 画像中已由本文件显式给出的键；测试据此比对剩余键是否被完整下发
_EXPLICIT_KEYS = frozenset({"extensions", "language", "locale_dirs", "gettext_compact", "version", "release"})


def _apply_profile(app, config):
    """把画像中未显式给出的键写入 ``config``（config-inited 阶段，先于任何消费者）。"""
    for name, value in _profile.items():
        if name not in _EXPLICIT_KEYS:
            setattr(config, name, value)


def setup(app):
    # 优先级 0 先于核心校验与各扩展的 config-inited 处理（500-900），
    # 让类型检查与路径校验看到最终取值。
    app.connect("config-inited", _apply_profile, priority=0)
    return _setup(app)

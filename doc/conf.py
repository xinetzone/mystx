#!/usr/bin/env python3
"""Sphinx 文档配置入口。

站点取值与装配顺序整体在 ``mystx.presets.mystx_docs``；本文件只做两件事：定位
仓库根目录，以及把画像分两段交给 Sphinx。

Sphinx 的契约是「conf.py 的模块命名空间即配置」：``sphinx.config`` 先 ``exec``
本文件，再以该命名空间构造 ``Config``。但只有少数键必须在那个时刻就位——
``extensions`` 用于加载扩展，``language`` / ``locale_dirs`` / ``gettext_compact``
用于初始化 i18n，都发生在 ``config-inited`` 之前；站点身份字段
（``project`` / ``author`` / ``copyright`` / ``version`` / ``release``）一并显式
给出，让 conf.py 保持一眼可见的站点门面。

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

# 早读键：Sphinx 在 config-inited 之前就要用，必须在模块层可见
extensions = _profile["extensions"]
language = _profile["language"]
locale_dirs = _profile["locale_dirs"]
gettext_compact = _profile["gettext_compact"]
project = _profile["project"]
author = _profile["author"]
copyright = _profile["copyright"]
version = _profile["version"]
release = _profile["release"]

# 由本集合界定哪些键已显式给出；测试据此比对画像是否被完整下发
_EARLY_KEYS = frozenset(
    {
        "extensions",
        "language",
        "locale_dirs",
        "gettext_compact",
        "project",
        "author",
        "copyright",
        "version",
        "release",
    }
)


def _apply_profile(app, config):
    """把画像中非早读的键写入 ``config``（config-inited 阶段，先于任何消费者）。"""
    for name, value in _profile.items():
        if name not in _EARLY_KEYS:
            setattr(config, name, value)


def setup(app):
    # 优先级 0 先于核心校验与各扩展的 config-inited 处理（500-900），
    # 让类型检查与路径校验看到最终取值。
    app.connect("config-inited", _apply_profile, priority=0)
    return _setup(app)

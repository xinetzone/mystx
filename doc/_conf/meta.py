"""项目元信息与国际化、本地化配置。"""
from __future__ import annotations

from mystx.utils import resolve_release

project = "mystx"
author = "xinetzone"
release = resolve_release("mystx", env_var="MYSTX_VERSION", fallback="0.0.0")
# epub 是 .readthedocs.yml 声明的 formats 之一，而 Sphinx 的 epub3 builder 要求
# copyright 与 version 均非空，否则构建期报「配置项不能为空」。RTD 侧已开
# fail_on_warning，这会直接把该 format 判红（实测复现）。version 取 release
# 即可：本包无 X.Y 短版本约定，取空值则 epub 产物的版本号本身也不合法。
version = release
copyright = "2026, xinetzone"

language = "zh_CN"
locale_dirs = ["../locales/"]
gettext_compact = False

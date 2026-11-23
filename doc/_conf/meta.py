"""项目元信息与国际化、本地化配置。"""
from mystx.utils import resolve_release

project = "mystx"
author = "xinetzone"
release = resolve_release("mystx", env_var="MYSTX_VERSION", fallback="0.0.0")
# epub3 builder 要求 copyright 与 version 非空；本包无 X.Y 短版本约定，故取 release
version = release
copyright = "2026, xinetzone"

language = "zh_CN"
locale_dirs = ["../locales/"]
gettext_compact = False

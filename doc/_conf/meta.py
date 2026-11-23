"""版本号与 i18n 设置（依赖运行期或初始化时序，无法放入 ``_config.toml``）。

``language`` / ``locale_dirs`` / ``gettext_compact`` 必须在 conf.py 读取阶段就位：
Sphinx 在 ``__init__`` 中先做 ``_init_i18n()``、后触发 ``config-inited``，
若走 ``_config.toml`` 的延迟合并，翻译不会被加载（实测标题退化为英文）。
其余站点元信息与外观取值已迁至 ``doc/_config.toml``。
"""
from mystx.utils import resolve_release

release = resolve_release("mystx", env_var="MYSTX_VERSION", fallback="0.0.0")
# epub3 builder 要求 copyright 与 version 非空；本包无 X.Y 短版本约定，故取 release
version = release

language = "zh_CN"
locale_dirs = ["../locales/"]
gettext_compact = False

from typing import Any

from ..config.defaults import build_base_config
from ..extensions import resolve_extensions
from ..myst_compat import register_hooks
from ..themes import resolve_theme, resolve_theme_options
from ..utils import deep_merge
from ._shared import build_project_meta, build_setup_closure


def build_config(override: dict[str, Any] | None = None) -> dict[str, Any]:
    """极简 MyST 预设：仅保留 ``myst_parser`` + 两个兼容性钩子。

    适用于轻量个人笔记、小型文档站点，不引入任何可选扩展。
    ``override`` 支持的核心键（与 okf_docs 预设保持字段名一致）：

    * ``project`` / ``author`` / ``release`` / ``version`` / ``language``
    * ``html_title`` / ``html_theme`` / ``html_theme_options``
    * ``extensions_required`` / ``extensions_optional``
    * ``config_override`` 其余任意 Sphinx 配置覆盖
    """
    params = dict(override or {})

    extensions = resolve_extensions(
        required=params.get("extensions_required", ("myst_parser",)),
        optional=params.get("extensions_optional", ()),
    )

    theme = params.get("html_theme") or resolve_theme()
    theme_options = resolve_theme_options(
        theme, params.get("html_theme_options")
    )

    params["html_theme"] = theme
    params["html_theme_options"] = theme_options
    params["extensions"] = extensions
    project_meta = build_project_meta(params)

    base = build_base_config(params)
    merged = deep_merge(base, project_meta)

    merged["setup"] = build_setup_closure(
        register_fns=[register_hooks],
        user_setup=params.get("setup"),
    )
    return merged

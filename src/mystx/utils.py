import importlib.util
import os
from typing import Any


def resolve_release(
    distribution: str = "mystx",
    *,
    env_var: str | None = None,
    fallback: str = "0.0.0",
) -> str:
    """解析包版本号，供 ``conf.py`` 的 ``release`` / ``version`` 使用。

    回退链：已安装分发包的元数据 → 环境变量 ``env_var`` → ``fallback``。
    覆盖「源码树内直接构建文档、包尚未安装」与「CI 以变量注入版本」两类
    场景，避免 ``conf.py`` 内联 try-except 样板。

    Args:
        distribution: 分发包名（非模块名）。
        env_var: 可选的版本环境变量名；未设置或为空时继续回退。
        fallback: 最终兜底值。
    """
    try:
        from importlib.metadata import version as _pkg_version

        return _pkg_version(distribution)
    except Exception:
        pass
    if env_var:
        value = os.environ.get(env_var)
        if value:
            return value
    return fallback


def sitemap_enabled_by_env() -> bool:
    """当前环境是否需要 mystx 自行生成 sitemap 所需配置。

    判定规则由包内唯一实现：GitHub Actions 有显式 baseurl；非 ReadTheDocs
    环境可回退到本地站点；ReadTheDocs 自带 sitemap 生成，故不注入。
    扩展启用判定与 ``html_baseurl`` 推断共用本函数，避免两处各写一遍分支。
    """
    return bool(os.environ.get("GITHUB_ACTIONS")) or not os.environ.get("READTHEDOCS")


def has_module(mod: str) -> bool:
    """探测模块是否可导入，不触发模块副作用。

    等价于原 conf.py 的 ``_has()``，但作为公共 API 导出供外部调用。
    基于 :func:`importlib.util.find_spec`，比 ``try-import`` 更轻量，
    不会触发被探测模块的顶层代码执行。
    """
    try:
        return importlib.util.find_spec(mod) is not None
    except (ImportError, ModuleNotFoundError):
        return False


def deep_merge(base: dict[str, Any], override: dict[str, Any] | None = None,
               *, remove_marker: Any = None) -> dict[str, Any]:
    """分层合并配置字典（公理 A1 实现）。

    规则：

    * ``override`` 中存在的键覆盖 ``base`` 同键；
    * 值为 ``remove_marker`` 的键（默认 ``None``）表示「从 base 中删除该键」——
      注意这与 Sphinx 原生「某键 = None 表示使用 Sphinx 默认」语义不同。
      若想表达「将某键显式置为 None 交给 Sphinx 默认处理」，请传
      ``sentinel`` 对象或其他非 ``remove_marker`` 的值；
    * 嵌套字典递归合并，其他类型直接替换。
    """
    override = override or {}
    result: dict[str, Any] = {}
    for k, v in base.items():
        if k in override and override[k] is remove_marker:
            continue
        if isinstance(v, dict) and k in override and isinstance(override[k], dict):
            result[k] = deep_merge(v, override[k], remove_marker=remove_marker)
        elif k in override:
            result[k] = override[k]
        else:
            result[k] = v
    for k, v in override.items():
        if k not in result and v is not remove_marker:
            result[k] = v
    return result

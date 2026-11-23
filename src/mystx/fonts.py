"""可选字体增强：存在则生效，缺失或失败仅记日志。

文档站常需要在构建期用 matplotlib 绘制带中文/表情字形的内容，而字体
配置依赖「字体包 + 字体目录」两项外部资源，二者在 CI（仅安装文档 extras）
与本地环境中的可用性不同。本模块把「守卫 + 静默降级」的样板收拢为一个
调用即可，任何一步不满足都只影响构建期绘图字形，不阻断构建。
"""

import importlib
from collections.abc import Iterable
from pathlib import Path

from sphinx.util import logging

from .utils import has_module

logger = logging.getLogger(__name__)

DEFAULT_FONT_MODULE = "taolib.fonts"
DEFAULT_FONT_FUNC = "configure_matplotlib_fonts"


def configure_optional_matplotlib_fonts(
    font_directory: str | Path,
    families: Iterable[str],
    *,
    module: str = DEFAULT_FONT_MODULE,
    func: str = DEFAULT_FONT_FUNC,
) -> bool:
    """尝试为 matplotlib 配置字体，失败时静默跳过。

    依次检查三项前置条件：字体包可导入、字体目录存在、调用无异常。
    任一不满足即记录一条 info 日志并返回 ``False``，绝不抛出——该配置
    只影响构建期 matplotlib 绘图的字形，不应成为构建的硬依赖。

    Args:
        font_directory: 字体文件所在目录。
        families: 字体族名序列，按优先级排列。
        module: 提供字体配置函数的模块名。
        func: 模块内的配置函数名，按关键字传入
            ``font_directory`` / ``families``。

    Returns:
        是否真正完成了字体配置。
    """
    directory = Path(font_directory)
    if not has_module(module):
        logger.info("[mystx] 未安装 %s，跳过 matplotlib 字体配置", module)
        return False
    if not directory.is_dir():
        logger.info("[mystx] 字体目录不存在，跳过 matplotlib 字体配置：%s", directory)
        return False
    try:
        configure = getattr(importlib.import_module(module), func)
        configure(font_directory=directory, families=tuple(families))
    except Exception as exc:
        logger.info("[mystx] matplotlib 字体配置未生效，已跳过：%s", exc)
        return False
    return True

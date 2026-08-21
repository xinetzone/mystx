#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主题管理模块

该模块负责mystx主题的注册和管理功能。
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from sphinx.application import Sphinx
from sphinx.util import logging

# 获取Sphinx日志记录器
logger = logging.getLogger(__name__)

@dataclass(slots=True)
class MySTX:
    """mystx主题管理类，负责整合主题信息管理和配置功能。
    
    该类负责查找主题目录、注册主题到Sphinx应用。
    
    Attributes:
        app: Sphinx应用实例，用于注册主题和连接事件。
        name: 主题名称，默认为"mystx"。
        theme_dir: 主题目录路径，初始化后自动设置。
    """
    app: Sphinx
    name: str = "mystx"
    theme_dir: Optional[str] = field(init=False)
    
    def __post_init__(self) -> None:
        """初始化后处理函数，查找主题目录并注册主题。
        
        此方法在类实例化后自动调用，负责确定主题目录的绝对路径，
        验证目录存在性，然后将主题注册到Sphinx应用。
        
        Raises:
            FileNotFoundError: 如果主题目录不存在。
        """
        # 确定主题目录的绝对路径
        parent = Path(__file__).parent.resolve()
        theme_dir = parent / "theme" / self.name
        
        # 验证主题目录是否存在
        if not theme_dir.exists():
            logger.error(f"主题目录未找到: {theme_dir}")
            raise FileNotFoundError(f"主题目录未找到: {theme_dir}")
        
        self.theme_dir = str(theme_dir)
        try:
            # 注册主题到Sphinx应用
            self.app.add_html_theme(self.name, self.theme_dir)
        except Exception as e:
            logger.error(f"注册 {self.name} 主题时发生错误: {e}", exc_info=True)
            raise
        
        logger.info(f"{self.name} 主题已成功注册")
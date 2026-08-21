#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块

该模块负责处理mystx主题的配置加载、应用和交互式功能设置。
"""

from dataclasses import dataclass
import tomllib
from pathlib import Path
from typing import Any, Dict, Optional
from sphinx.application import Sphinx
from sphinx.util import logging
from sphinx.config import Config
from sphinx.errors import ExtensionError
from .version_switcher import sphinx_setup as version_switcher_setup

# 获取Sphinx日志记录器
logger = logging.getLogger(__name__)

@dataclass(slots=True)
class ConfigManager:
    """配置管理器，负责处理主题相关的配置加载和应用。

    该类提供了从TOML文件加载配置、合并自定义与用户配置
    以及应用配置到Sphinx实例的功能。

    Attributes:
        app: Sphinx 应用实例，用于获取源目录并读取配置。
        config: Sphinx 配置对象，用于应用自定义主题选项。
    """
    app: Sphinx
    config: Config
    logger: Optional[logging.SphinxLoggerAdapter] = None
    
    def __post_init__(self) -> None:
        """初始化日志记录器"""
        self.logger = logging.getLogger(f"{__name__}.ConfigManager")
        
    def load_custom_config(self) -> Optional[Dict[str, Any]]:
        """加载自定义配置文件。
        
        Returns:
            配置字典，如果文件不存在则返回None
        """
        custom_toml = Path(self.app.srcdir) / "_config.toml"
        if not custom_toml.exists():
            return None
        
        self.logger.info(f"找到自定义配置文件 {custom_toml}")
        try:
            with open(custom_toml, "rb") as f:
                custom_config = tomllib.load(f)
                self.logger.info(f"成功加载自定义配置文件 {custom_toml}")
                return custom_config
        except tomllib.TOMLDecodeError as e:
            self.logger.error(f"自定义配置文件格式错误: {e}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"加载自定义配置文件时出错: {e}", exc_info=True)
            raise
    
    def apply_config(self) -> None:
        """应用加载的配置到Sphinx配置对象。
        
        主要处理html_theme_options的合并。
        """
        custom_config = self.load_custom_config()
        if not custom_config:
            return
        
        self._merge_html_theme_options(custom_config)
        
    def _merge_html_theme_options(self, custom_config: Dict[str, Any]) -> None:
        """合并自定义配置到html_theme_options。"""
        if "html_theme_options" not in custom_config:
            return
        
        if not hasattr(self.config, "html_theme_options"):
            self.config.html_theme_options = {}
        
        # 合并自定义配置到html_theme_options
        for key, value in custom_config["html_theme_options"].items():
            if key not in self.config.html_theme_options:
                self.config.html_theme_options[key] = value
                self.logger.debug(f"应用自定义配置: {key} = {value}")
            # 对二级字典进行递归合并
            elif isinstance(value, dict) and isinstance(self.config.html_theme_options[key], dict):
                for sub_key, sub_value in value.items():
                    if sub_key not in self.config.html_theme_options[key]:
                        self.config.html_theme_options[key][sub_key] = sub_value
                        self.logger.debug(f"应用嵌套自定义配置: {key}.{sub_key} = {sub_value}")
        
        self.logger.info("已成功更新html_theme_options配置")


def thebe_setup(app: Sphinx, config: Config) -> None:
    """配置Sphinx文档的Thebe交互式代码块功能。
    
    Args:
        app: Sphinx应用实例
        config: Sphinx配置对象
    """
    logger = logging.getLogger(f"{__name__}.thebe_setup")
    logger.info("配置Thebe交互式代码块功能")
    
    # 确保必要的配置结构存在
    if not hasattr(config, "html_theme_options"):
        config.html_theme_options = {}
    
    if "launch_buttons" not in config.html_theme_options:
        config.html_theme_options["launch_buttons"] = {}
    
    # 启用Thebe按钮
    config.html_theme_options["launch_buttons"]["thebe"] = True
    logger.debug("已启用Thebe交互式代码块功能")
    
    # 使用Sphinx的app.setup_extension方法添加sphinx_thebe扩展
    if "sphinx_thebe" not in config.extensions:
        try:
            app.setup_extension("sphinx_thebe")
            logger.info("已成功设置sphinx_thebe扩展")
        except ExtensionError as e:
            logger.warning(f"设置sphinx_thebe扩展时出错: {e}")
    else:
        logger.debug("sphinx_thebe扩展已存在，无需重复设置")


def config_inited_handler(app: Sphinx, config: Config) -> None:
    """config-inited 事件处理器
    
    在 Sphinx 完成配置对象（Config）初始化后立即触发，让你有机会在构建器（Builder）创建之前，读取或修改配置。
    
    触发时机:
        - 发生在：conf.py 执行完毕，所有配置变量已收集并封装到 Config 对象中。
        - 早于：builder-inited（构建器初始化）事件。
        - 晚于：扩展加载（extensions 列表中的扩展已导入）。
            - 因为 extensions 已经加载完毕，所以在 config-inited 中修改 extensions 列表不会重新加载扩展。
              如果需要动态加载扩展，应使用 app.setup_extension()。
    
    Args:
        app: Sphinx应用实例
        config: Sphinx配置对象
    """
    event_logger = logging.getLogger(__name__)
    event_logger.info("初始化mystx配置系统")
    
    try:
        # 加载并应用自定义配置
        config_manager = ConfigManager(app=app, config=config)
        config_manager.apply_config()
        
        # 设置Thebe功能开关
        app.add_config_value("use_thebe", False, "html")  # 默认禁用
        use_thebe = getattr(config, "use_thebe", False)  # 默认禁用
        if use_thebe:
            # 配置Thebe功能
            thebe_setup(app, config)
            event_logger.debug("Thebe功能已开启")
        else:
            event_logger.debug("Thebe功能已禁用")
        
        # 设置版本切换器
        app.add_config_value("version_switcher_json_url", "", "html")  # 默认禁用
        version_switcher_json_url = getattr(config, "version_switcher_json_url", "")  # 默认禁用
        if version_switcher_json_url:
            version_switcher_setup(app, config)
            event_logger.debug("版本切换器已配置")
        else:
            event_logger.debug("版本切换器已禁用")
    except Exception as e:
        event_logger.error(f"配置系统初始化失败: {e}", exc_info=True)
        raise

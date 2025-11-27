# MySTX

![repo size](https://img.shields.io/github/repo-size/xinetzone/mystx.svg)
[![PyPI][pypi-badge]][pypi-link]
[![GitHub issues][issue-badge]][issue-link]
[![GitHub forks][fork-badge]][fork-link]
![atom star](https://gitcode.com/flexloop/mystx/star/badge.svg)
[![GitHub stars][star-badge]][star-link]
[![GitHub license][license-badge]][license-link]
[![contributors][contributor-badge]][contributor-link]
[![Documentation Status][status-badge]][status-link]
[![Downloads][download-badge]][download-link]
[![PyPI - Downloads][install-badge]][install-link]

[pypi-badge]: https://img.shields.io/pypi/v/mystx.svg
[pypi-link]: https://pypi.org/project/mystx/
[issue-badge]: https://img.shields.io/github/issues/xinetzone/mystx
[issue-link]: https://github.com/xinetzone/mystx/issues
[fork-badge]: https://img.shields.io/github/forks/xinetzone/mystx
[fork-link]: https://github.com/xinetzone/mystx/network
[star-badge]: https://img.shields.io/github/stars/xinetzone/mystx
[star-link]: https://github.com/xinetzone/mystx/stargazers
[license-badge]: https://img.shields.io/github/license/xinetzone/mystx
[license-link]: https://github.com/xinetzone/mystx/LICENSE
[contributor-badge]: https://img.shields.io/github/contributors/xinetzone/mystx
[contributor-link]: https://github.com/xinetzone/mystx/contributors
[status-badge]: https://readthedocs.org/projects/mystx/badge/?version=latest
[status-link]: https://mystx.readthedocs.io/zh-cn/latest/?badge=latest
[download-badge]: https://pepy.tech/badge/mystx
[download-link]: https://pepy.tech/project/mystx
[install-badge]: https://img.shields.io/pypi/dw/mystx?label=pypi%20installs
[install-link]: https://pypistats.org/packages/mystx

**MySTX** 是基于 Sphinx Book Theme 的现代化、可定制的 Sphinx HTML 主题，为技术文档提供优雅美观的展示效果。它结合了现代Web设计理念与优秀的阅读体验，使您的文档既专业又易于阅读。

## ✨ 特性

- 🎨 基于 Sphinx Book Theme 的现代化设计风格
- 🛠️ 灵活的主题配置系统，支持从 TOML 文件加载主题配置选项
- 📝 完善的 MyST Markdown 和 Jupyter Notebook 支持
- 🚀 简单易用的主题注册和配置应用流程
- 📚 丰富的可选扩展，用于增强文档功能

## 🔧 安装

### 基本安装

使用 pip 安装 mystx 主题：

```bash
pip install mystx
```

### 安装文档扩展

如果需要使用文档扩展功能，可以安装可选依赖：

```bash
pip install "mystx[doc]"
```

### 开发环境安装

对于开发者，可以安装开发依赖：

```bash
pip install -ve .[dev]
```

## 📋 依赖

### 核心依赖

- `sphinx-book-theme>=1.1.4` (主题继承)
- `sphinx>=8.0.0` (文档生成引擎)
- `myst-nb` (Jupyter Notebook 支持)
- `myst-parser` (MyST Markdown 解析器)
- Python 3.12+ (运行环境)

## 🚀 快速开始

在您的 Sphinx 项目的 `conf.py` 文件中，添加以下配置来使用 `mystx` 主题：

```python
# conf.py
project = "mystx 文档" # 文档项目名称
author = "xinetzone" # 文档作者
# == 国际化与本地化设置 ==================================================================
language = 'zh_CN' # 文档语言（中文简体）
locale_dirs = ['../locales/'] # 翻译文件存放目录
gettext_compact = False # 是否合并子目录的PO文件（False表示不合并）
# 插件
extensions = ['mystx']
html_last_updated_fmt = '%Y-%m-%d, %H:%M:%S'  # 文档的最后更新时间格式
# 排除文件和目录模式
exclude_patterns = [
    "_build",  # 构建输出目录
    "Thumbs.db",  # 缩略图数据库
    ".DS_Store",  # macOS 系统文件
]
static_path = ["_static"]  # 静态资源目录，用于存放CSS、JavaScript、图片等
html_theme = 'mystx'  # 使用的主题名称
html_logo = "_static/images/logo.jpg" # 文档logo
html_title = "Sphinx mystx Theme" # 文档标题
html_copy_source = True # 是否在文档中包含源文件链接
html_favicon = "_static/images/favicon.jpg" # 文档favicon
```

## ⚙️ 配置指南

mystx 主题提供了丰富的配置选项，让您可以根据项目需求自定义文档外观和功能。以下是配置指南：

### 主题选项

mystx 主题支持通过两种方式配置主题选项：

#### 方式一：在 `conf.py` 文件中配置

在 Sphinx 项目的 `conf.py` 文件中，使用 `html_theme_options` 字典配置各种主题选项：

```python
html_theme_options = {
    # 仓库相关配置
    "repository_url": "https://github.com/yourusername/yourproject",  # 项目仓库地址
    "use_repository_button": True,  # 在页眉显示指向存储库的小 GitHub 徽标
    "use_issues_button": True,  # 是否显示问题反馈按钮
    "use_edit_page_button": True,  # 是否显示编辑页面按钮
    "path_to_docs": "doc/",  # 文档目录（相对于项目根目录）
    
    # 导航相关配置
    "home_page_in_toc": false,  # 是否在目录中显示首页
    "show_navbar_depth": 2,  # 导航栏显示的层级深度
    
    # 其他配置
}
```

#### 方式二：通过 `_config.toml` 文件配置

您也可以在项目根目录创建 `_config.toml` 文件，使用 TOML 格式配置主题选项：

```toml
[html_theme_options]
# 仓库相关配置
repository_url = "https://github.com/yourusername/yourproject"
use_repository_button = true
use_issues_button = true
use_edit_page_button = true
path_to_docs = "doc/" # 文档目录（相对于项目根目录）

# 导航相关配置
home_page_in_toc = false # 是否在目录中显示首页
show_navbar_depth = 2 # 导航栏显示的层级深度

# 其他配置
```

您可以根据实际需求选择性配置上述选项，未配置的选项将使用默认值。

## 📚 文档

请访问 [mystx 官方文档](https://mystx.readthedocs.io/zh-cn/latest/) 以及 [daobook/sphinx-book-theme](https://github.com/daobook/sphinx-book-theme)的[Sphinx Book Theme 文档](https://daobook.github.io/sphinx-book-theme/) 了解更多详细信息和使用示例。

## 🔗 链接

- [GitHub 仓库](https://github.com/xinetzone/mystx)
- [PyPI 项目页面](https://pypi.org/project/mystx/)
- [官方文档](https://mystx.readthedocs.io/)
- [问题反馈](https://github.com/xinetzone/mystx/issues)

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

**MySTX** 是基于 pydata-sphinx-theme 的书籍化 Sphinx HTML 主题，借鉴 sphinx-book-theme 的阅读体验（全书导航、页眉工具箱、边注），为技术文档提供连续阅读的排版。

## ✨ 特性

- 🎨 基于 pydata-sphinx-theme 的基座 + 书籍化阅读层
- 🛠️ 6 个书籍层选项 + pydata 原生选项，取值集中在 theme.toml
- 📚 全书侧栏：每页渲染完整目录，而不是只显示当前章节子树
- 🔗 页眉工具箱：下载 / 全屏 / 源码 / 编辑 / issue / 仓库
- 📝 边注与 `{margin}` 块：脚注搬到右侧留白，窄屏折叠为点击展开

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

- `pydata-sphinx-theme>=0.24,<0.25` (主题基座)
- `sphinx>=8.2,<10` (文档生成引擎)
- Python 3.11+ (运行环境)

mystx 只依赖上面两项。MyST Markdown (`myst-parser`) 与 Notebook (`myst-nb`)
是可选扩展，按需装在自己的项目里。

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
html_static_path = ["_static"]  # 静态资源目录，用于存放CSS、JavaScript、图片等
html_theme = 'mystx'  # 使用的主题名称
html_logo = "_static/images/logo.jpg" # 文档logo
html_title = "Sphinx mystx Theme" # 文档标题
html_copy_source = True # 是否在文档中包含源文件链接
html_favicon = "_static/images/favicon.jpg" # 文档favicon
```

## ⚙️ 配置指南

mystx 主题提供了丰富的配置选项，让您可以根据项目需求自定义文档外观和功能。以下是配置指南：

### 主题选项

书籍层选项写在 `conf.py` 的 `html_theme_options` 里，未写的取 `theme.toml` 默认值：

```python
html_theme_options = {
    "book_nav_scope": "book",       # book 全书树 / section 当前章节
    "book_nav_depth": 3,            # 侧栏初始展开层数
    "book_content_width": "46rem",  # 正文最大宽度
    "book_header_buttons": ["download", "fullscreen", "source", "edit", "issue", "repo"],
    "book_use_sidenotes": False,    # 脚注转边注
    "book_footer_items": ["author", "copyright", "last-updated"],
}
```

页眉的源码 / 编辑 / issue / 仓库按钮需要仓库坐标（与 pydata-sphinx-theme 的约定一致）：

```python
html_context = {
    "github_user": "xinetzone",
    "github_repo": "mystx",
    "github_version": "main",
    "doc_path": "doc",
}
```

其余选项（`navbar_*`、`secondary_sidebar_items`、`navigation_depth` 等）直接透传给
pydata-sphinx-theme。完整清单与默认值见文档站的「选项参考」。

## 📚 文档

请访问 [mystx 官方文档](https://mystx.readthedocs.io/zh-cn/latest/) 以及 [daobook/sphinx-book-theme](https://github.com/daobook/sphinx-book-theme)的[Sphinx Book Theme 文档](https://daobook.github.io/sphinx-book-theme/) 了解更多详细信息和使用示例。

## 🔗 链接

- [GitHub 仓库](https://github.com/xinetzone/mystx)
- [PyPI 项目页面](https://pypi.org/project/mystx/)
- [官方文档](https://mystx.readthedocs.io/)
- [问题反馈](https://github.com/xinetzone/mystx/issues)

# MySTX 文档

> **MySTX** 是基于 Sphinx Book Theme 的现代化、可定制 Sphinx HTML 主题，
> 附带一组增强文档体验的扩展（GitHub 统计卡片、MyST 实时预览等）。
> 本页是文档集的根入口，承担**定位与导航**；各子区的事实与数字以子区
> `index.md` 为唯一权威陈述位置，本页不重复。

## 文档地图

| 区域 | 内容 | 入口 |
|---|---|---|
| `ext/` | mystx 自带扩展的使用文档（指令、选项、示例） | [ext/index.md](ext/index.md) |
| `gallery/` | 相关项目与插件画廊（DaoBook、Executable Books、Sphinx 扩展等） | [gallery/index.md](gallery/index.md) |
| `tests/` | 交互式演示（Jupyter Notebook / Thebe） | [tests/index.md](tests/index.md) |
| `autoapi/` | mystx 包的 API 参考（由 autoapi 自动生成） | 构建后自动产出 |

## 阅读路径

按读者意图任选一条，不必从头读：

| 我想…… | 从这里开始 |
|---|---|
| 用 mystx 主题构建自己的文档 | [README 快速开始](https://github.com/xinetzone/mystx#快速开始) |
| 配置主题选项（仓库按钮、导航深度、页脚等） | [`_config.toml`](_config.toml) + [README 配置指南](https://github.com/xinetzone/mystx#%EF%B8%8F-配置指南) |
| 在文档里嵌入 GitHub 统计卡片 | [ext/github-readme-stats/index.md](ext/github-readme-stats/index.md) |
| 在线试写 MyST 并实时预览 | [ext/live-preview/index.md](ext/live-preview/index.md) |
| 查 mystx 包的 Python API | 构建产物 `autoapi/`（由 `conf.py` 中 `autoapi.extension` 生成） |
| 看 Sphinx 生态相关项目 | [gallery/index.md](gallery/index.md) |

## 相关入口

- 仓库 README（安装、特性、徽章）：[../README.md](../README.md)
- GitHub 仓库：<https://github.com/xinetzone/mystx>
- PyPI：<https://pypi.org/project/mystx/>
- 上游父主题（daobook/sphinx-book-theme）：<https://daobook.github.io/sphinx-book-theme/>

## 索引与搜索

- {ref}`genindex` — 所有索引条目
- {ref}`modindex` — 模块索引
- {ref}`search` — 搜索文档内容

```{toctree}
:hidden:
:maxdepth: 2

ext/index
gallery/index
tests/index
```

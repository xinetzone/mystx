# mystx 扩展

> 本目录收录 **mystx 自带扩展**的使用文档。mystx 除提供主题外，还打包了若干
> Sphinx 扩展，用于增强文档的可视化与交互能力。
>
> 注意：本目录（`ext/`）存放的是**扩展的使用文档**；Sphinx 构建时加载的自定义
> 扩展代码位于 [`../_ext/`](../_ext/)（Python 模块），两者职责不同。

## 扩展清单

| 扩展 | 模块 | 用途 | 入口 |
|---|---|---|---|
| GitHub Readme Stats | `mystx.ext.github_readme_stats` | 在文档中嵌入 GitHub 用户统计、常用语言、置顶仓库、WakaTime 卡片 | [github-readme-stats/index.md](github-readme-stats/index.md) |
| MyST 实时预览 | —（基于 `sphinx-pyscript`） | 在浏览器内编辑 MyST 文本并实时查看 HTML/AST/LaTeX 输出 | [live-preview/index.md](live-preview/index.md) |

## 阅读路径

| 我想…… | 从这里开始 |
|---|---|
| 在自己的文档里放 GitHub 统计卡片 | [github-readme-stats/index.md](github-readme-stats/index.md) |
| 在线试写 MyST 语法 | [live-preview/index.md](live-preview/index.md) |
| 查看扩展的 Python API | 构建产物 `autoapi/mystx/ext/` |

```{toctree}
:hidden:
:maxdepth: 2

github-readme-stats/index
live-preview/index
```

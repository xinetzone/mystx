# 交互式演示

> 本目录收录 mystx 文档的**交互式演示**，用于展示 MyST Notebook、Thebe 等
> 扩展在 mystx 主题下的渲染效果。演示内容为功能验证，非使用教程。

## 演示清单

| 演示 | 格式 | 内容 | 入口 |
|---|---|---|---|
| 测试文档 | Jupyter Notebook | MyST Notebook 渲染、Thebe 代码单元格交互 | [test.ipynb](test.ipynb) |

## 说明

- 演示依赖 `myst-nb`（Notebook 解析）与 `sphinx-thebe`（在线执行），均在
  `conf.py` 中按环境降级加载。
- 如需在本地复现演示，确保已安装 `mystx[doc]` 可选依赖。

```{toctree}
:hidden:
:maxdepth: 1

test
```

---
title: 用 Markdown 写文档
---

# 用 Markdown 写文档

站点装了 `myst-parser`，`guide/index.rst` 的 toctree 里可以直接写 `.md` 文件名。RST 与
Markdown 混用没有副作用：两者最后都变成同一套 docutils 节点，主题侧的边注、页眉按钮、
页脚接管都只认节点类型，不区分源文件格式。

## 为什么是 MyST 而不是 CommonMark

普通 Markdown 没有 Sphinx 需要的交叉引用、指令和角色。MyST 是 Markdown 的超集，用
「指令块 + 角色语法」补上这些，同时保留 Markdown 的书写手感：

````markdown
```{note}
这是一个指令块；冒号围栏写法需要 `colon_fence` 扩展。
```
````

标题层级直接映射成文档结构，`#` 是文档标题，`##` 开始是小节。不要跳过层级，否则
「本页目录」会缺一级。

## 脚注会变成边注

边注功能在 Markdown 里同样可用，写法和 Markdown 原生脚注一致：

````markdown
正文里的引用点[^note1]。

[^note1]: 这段话会被搬到页面右侧，窄屏时折回正文流。
````

本页末尾就挂了一个真脚注，可以直接看效果[^demo]。

## 表格与代码块

Markdown 表格走 GFM 表格实现，列宽由浏览器决定，不必像 RST grid table 那样手工对齐
边框——写中文表格时这点省事不少。

## 什么情况还是写 RST

需要精确控制列宽、或者要用 RST 独有的指令参数时，继续写 RST。主题不强制一种格式，
两种并存是常态。

[^demo]: 这条脚注在宽屏下会出现在右侧边栏区，窄屏下需要点引用号才展开。

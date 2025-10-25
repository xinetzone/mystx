---
py-config:
  splashscreen:
    autoclose: true
  packages:
    - myst-docutils==4.0
    - docutils==0.20
    - pygments
---

# ⚡ 实时预览

这是 MyST Markdown [docutils 渲染器](docutils.md) 的实时预览。
你可以在下方编辑文本/配置，并查看实时输出。

```{py-script}
:file: live_preview.py
```

::::::::{grid} 1 1 2 2

:::::::{grid-item}
:child-align: start

```{raw} html
<div><u><span id="myst-version">myst-parser v</span></u></div>
```

:::::{tab-set}
:class: preview-input-tabs

::::{tab-item} 输入文本
:class-container: sd-h-100
:class-content: sd-h-100

````{raw} html
<textarea class="pyscript input" id="input_myst">
(heading-1)=
# 标题 1

哈喽，世界！

```{note}
一个提示性注释！
```

[链接到该标题](#heading-1)

## 代码

```python
from package import module
module.call("string")
```

## 定义列表

术语
: 定义

## 数学

$$\pi = 3.14159$$

## 图像

```{figure} https://via.placeholder.com/150
:width: 100px
:align: center

图像说明
```

## 表格

```{list-table}
:header-rows: 1
:align: center

* - 表头 1
  - 表头 2
* - 条目 1 a
  - 条目 2 a
* - 条目 1 b
  - 条目 2 b
```
</textarea>
````

::::
::::{tab-item} 配置（YAML）
:class-container: sd-h-100
:class-content: sd-h-100

<textarea class="pyscript input" id="input_config">
myst_enable_extensions:
- colon_fence
- deflist
- dollarmath
myst_heading_anchors: 2
myst_highlight_code_blocks: true
</textarea>
::::
:::::

:::::::
:::::::{grid-item}
:child-align: start

```{raw} html
<div class="display-flex">
<label for="output_format" class="display-inline-block">输出格式：</label>
<select id="output_format" class="display-inline-block">
  <option value="pseudoxml">AST</option>
  <option value="html5" selected>HTML</option>
  <option value="latex">LaTeX</option>
</select>
</div>
```

::::{tab-set}
:::{tab-item} HTML 渲染
<div class="pyscript" id="output_html"></div>
:::
:::{tab-item} 原始输出
<textarea class="pyscript output" id="output_raw" readonly="true"></textarea>
:::
:::{tab-item} 警告
<textarea class="pyscript output" id="output_warnings" readonly="true"></textarea>
:::
::::
:::::::
::::::::

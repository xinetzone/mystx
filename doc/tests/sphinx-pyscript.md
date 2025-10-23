---
py-config:
  splashscreen:
    autoclose: true
  packages:
  - matplotlib
---

# Sphinx PyScript

Sphinx PyScript 允许您在文档中使用 PyScript。使用 pip 安装：
```bash
pip install sphinx-pyscript
```
用法：
将插件添加到您的 `conf.py` :
```python
extensions = [
    "sphinx_pyscript",
]
```

要在页面上加载 PyScript，可以使用 py-config 指令以 YAML 格式加载配置：
```yaml
.. py-config::

    splashscreen:
        autoclose: true
    packages:
    - matplotlib
```

或者 MyST，使用 top-matter：

```
---
py-config:
  splashscreen:
    autoclose: true
  packages:
  - matplotlib
---
```

## `py-repl` 和 `py-terminal`

可以创建 REPL，使其将输出写入 `div` 中，并将 `stdout` 打印到终端，如下：

````md
```{py-repl}
:output: replOutput

print("hallo world")
import matplotlib.pyplot as plt
plt.plot([1, 2, 3])
plt.gcf()
```

<div id="replOutput"></div>

```{py-terminal}
```
````

按下 `Shift+Enter` 运行代码。

```{py-repl}
:output: replOutput

print("你好！")
import matplotlib.pyplot as plt
plt.plot([1, 2, 3])
plt.gcf()
```

<div id="replOutput"></div>

```{py-terminal}
```

## `py-script` application

下面是使用 `py-script` 指令将“a”替换为“b”的简单应用：

````md
```{py-script}
:file: convert_json_to_toml.py
```

<form method="post">
    <label for="input_text" style="display: block">Input</label>
    <textarea id="input_text" name="input_text" style="width: 90%">a</textarea>
    <label for="output_text" style="display: block">Output</label>
    <textarea id="output_text" name="output_text" readonly="true" style="width: 90%">b</textarea>
</form>
````
    
使用以下代码：

```{literalinclude} convert_json_to_toml.py
:language: python
```

```{py-script}
:file: convert_json_to_toml.py
```

<form method="post">
    <label for="input_text" style="display: block">Input</label>
    <textarea id="input_text" name="input_text" style="width: 90%">a</textarea>
    <label for="output_text" style="display: block">Output</label>
    <textarea id="output_text" name="output_text" readonly="true" style="width: 90%">b</textarea>
</form>

安装
====

从 PyPI 安装：

.. code-block:: console

   pip install mystx

如需在当前仓库开发：

.. code-block:: console

   pip install -e ".[dev]"

最小配置
--------

在 ``conf.py`` 中注册扩展并指定主题：

.. code-block:: python

   extensions = ["mystx"]
   html_theme = "mystx"
   html_title = "我的文档"

mystx 会在 ``setup()`` 中完成三件事：注册主题目录、注册样式表、连接书籍层钩子。
不需要再配置 ``html_theme_path`` 或 ``html_theme_options`` 的必填项。

验证
----

.. code-block:: console

   sphinx-build -b html doc _build/html

构建成功后：

- 页面左侧出现全书目录（默认展开 3 层）
- 顶部不再有站点级导航条，也没有面包屑
- 正文最大宽度为 ``46rem`` （可用 ``book_content_width`` 调整）

依赖边界
--------

mystx 自身只依赖 ``sphinx`` 与 ``pydata-sphinx-theme``。以下能力由站点按需安装：

- MyST Markdown：``myst-parser``
- Notebook：``myst-nb`` （同时会带上 ``myst-parser``）
- 在线运行：``sphinx-thebe``

这些扩展与主题无耦合：主题只负责 HTML 结构与样式。

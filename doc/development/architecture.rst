架构
====

继承链只有一层：

.. code-block:: text

   mystx
   └── inherit = pydata_sphinx_theme
       └── inherit = basic

mystx 不复制父主题的 ``layout.html``，只在必要处覆盖，并通过事件挂载书籍层。

构建期发生了什么
----------------

.. list-table::
   :header-rows: 1
   :widths: 26 74

   * - 阶段
     - mystx 的动作
   * - ``setup()``
     - 注册主题目录、注册 ``css/book.css``、连接两个事件
   * - ``builder-inited``
     - 归一化 ``book_*`` 选项；校验 ``book_nav_scope``；把侧栏参数函数注入 Jinja
   * - ``html-page-context``
     - 解析导航范围（``section`` 无祖先时回退 ``book``）；生成页眉按钮数据
   * - 模板渲染
     - ``layout.html`` 注入宽度变量；``book-nav.html`` 调用 ``generate_toctree_html``

源码布局
--------

.. code-block:: text

   src/mystx/
   ├── __init__.py              setup()：主题注册 + 事件连接
   ├── book/
   │   ├── nav.py               侧栏参数纯函数
   │   ├── buttons.py           页眉按钮数据与 URL 规则
   │   └── options.py           选项归一化、逐页 scope、按钮注入
   └── theme/mystx/
       ├── theme.toml           inherit + 默认选项 + sidebars
       ├── layout.html          只覆盖 extrahead
       ├── book-nav.html        侧栏组件
       ├── book-header-buttons.html  页眉工具箱
       └── static/              css/book.css、js/book.js

为什么组件要单独命名
--------------------

pydata-sphinx-theme 在 ``setup()`` 中会把自己的 ``components/`` 追加到
``config.templates_path``。站点模板路径的优先级高于子主题目录，因此：

- 子主题若使用与父主题同名的组件（如 ``sidebar-nav-bs.html``），会被父主题版本遮蔽；
- 唯一命名（``book-nav.html``）可以保证子主题模板生效。

不用父主题同名组件的代价是：父主题那套“空侧栏自动移除”逻辑不会作用于本组件。
mystx 用逐页 scope 解析补上这一点。

与 sphinx-book-theme 的关系
---------------------------

mystx 不依赖 sphinx-book-theme，也不继承它。后续能力按“数据协议 / 模板 /
Python 变换 / 样式”四件移植，并在 ``NOTICE`` 中保留归属。

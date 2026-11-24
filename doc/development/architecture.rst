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
     - 解析导航范围（``section`` 无祖先时回退 ``book``）；生成页眉按钮数据；
       生成页脚条目；检测页面是否含边注，决定是否让出右侧目录栏
   * - 模板渲染
     - ``layout.html`` 注入宽度变量并接管页脚；``book-nav.html`` 调用
       ``generate_toctree_html``
   * - ``post-transform``
     - ``FootnoteToSidenote`` （优先级 1，仅 html）把脚注换成边注节点

源码布局
--------

.. code-block:: text

   src/mystx/
   ├── __init__.py              setup()：主题注册 + 事件连接
   ├── book/
   │   ├── nav.py               侧栏参数纯函数
   │   ├── buttons.py           页眉按钮数据与 URL 规则
   │   ├── footer.py            页脚条目数据
   │   ├── options.py           选项归一化、逐页 scope、按钮注入、边注页面检测
   │   └── sidenotes.py         边注节点 + 脚注变换 + {margin} 指令
   └── theme/mystx/
       ├── theme.toml           inherit + 默认选项 + sidebars
       ├── layout.html          覆盖 extrahead、body_tag 与 footer
       ├── book-nav.html        侧栏组件
       ├── book-header-buttons.html  页眉工具箱
       ├── book-footer.html     内容页脚
       └── static/              css/{book,sidenotes,notebook}.css、js/book.js

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

边注层借鉴了 sphinx-book-theme 的 ``SideNoteNode`` / ``HandleFootnoteTransform`` /
``Margin`` 三个对象（BSD-3-Clause），但在 mystx 里重写并做了三处收紧：

- 引用找不到对应脚注、或脚注没有正文时跳过该条，不抛异常；
- 多条引用指向同一条脚注时各得一份副本，不会把内容搬空；
- ``{margin}`` 指令与样式常驻，开关只控制脚注变换。

边注布局
--------

宽屏下边注要占用正文右侧的留白，而这块区域通常属于右侧目录栏。mystx 的处理：

1. ``html-page-context`` 检查 doctree 中是否存在 ``sidenote`` / ``marginnote`` /
   ``margin`` 类节点，命中时给 ``<body>`` 加 ``mystx-has-margin``；
2. 只有这类页面在 ``>=1400px`` 时隐藏右侧目录栏，并让正文容器宽出留白列；
3. 边注以浮动 + 负右边距进入留白列，``clear: right`` 防止连续边注重叠；
4. 窄屏隐藏浮动内容，改为 ``label`` + ``input[type=checkbox]`` 点击展开。

因此同一站点里，含边注的页面不显示页内目录，纯正文页面不变。

配置
====

配置分两层：

1. ``theme.toml`` 中的默认值（随包发布，不需要站点重复声明）
2. 站点 ``conf.py`` 的 ``html_theme_options`` （只写覆盖项）

站点覆盖示例：

.. code-block:: python

   html_theme = "mystx"
   html_theme_options = {
       "book_nav_scope": "book",
       "book_nav_depth": 3,
       "book_content_width": "52rem",
   }

书籍层选项
----------

.. list-table::
   :header-rows: 1
   :widths: 26 16 14 44

   * - 选项
     - 类型
     - 默认
     - 作用
   * - ``book_nav_scope``
     - str
     - ``book``
     - ``book`` 渲染全书树；``section`` 只渲染当前章节子树
   * - ``book_nav_depth``
     - int
     - ``3``
     - 侧栏初始展开层数
   * - ``book_content_width``
     - str
     - ``46rem``
     - 正文最大宽度，写入 CSS 变量
   * - ``book_header_buttons``
     - list
     - 6 个按钮
     - 页眉按钮及顺序（P2 实现，当前无效）
   * - ``book_use_sidenotes``
     - bool
     - ``False``
     - 脚注转边注（P3 实现，当前无效）
   * - ``book_footer_items``
     - list
     - 3 项
     - 内容页脚组件（后续实现）

列表选项既可以写字符串（逗号分隔），也可以写列表：

.. code-block:: python

   html_theme_options = {
       "book_header_buttons": "download, source, edit",
       # 等价于 ["download", "source", "edit"]
   }

继承自基座的选项
----------------

``navbar_*``、``secondary_sidebar_items``、``navigation_depth``、
``show_nav_level``、``collapse_navigation``、``icon_links``、``switcher`` 等
均直接透传给 pydata-sphinx-theme，语义与其文档一致。

mystx 的默认值只做三处改动：

- ``navbar_start`` / ``navbar_center`` / ``navbar_end`` / ``navbar_persistent`` 置空
- ``article_header_start`` 置空（去掉面包屑）
- ``secondary_sidebar_items`` 只保留 ``page-toc``

要恢复顶部导航，显式赋值即可：

.. code-block:: python

   html_theme_options = {
       "navbar_center": ["navbar-nav"],
   }

页内覆盖
--------

PST 的页面级元数据仍然有效，例如去掉某页的右侧栏：

.. code-block:: markdown

   ---
   html_theme.sidebar_secondary.remove: true
   ---

主题名
------

``html_theme = "mystx"``。若同时安装了 ``pydata_sphinx_theme``，两者互不冲突：
mystx 只在自己的模板目录里覆盖，其余全部回退到基座。

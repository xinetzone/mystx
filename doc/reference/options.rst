选项参考
========

全部选项写在 ``html_theme_options`` 中，模板通过 ``theme_<选项名>`` 读取。
本页列出 mystx 自有选项与改过默认值的基座选项；未列出的基座选项保持原语义。

自有选项（6 个）
----------------

.. list-table::
   :header-rows: 1
   :widths: 26 12 20 42

   * - 选项
     - 类型
     - 默认值
     - 备注
   * - ``book_nav_scope``
     - str
     - ``"book"``
     - ``book`` / ``section``；非法值回退 ``book`` 并告警
   * - ``book_nav_depth``
     - int
     - ``3``
     - 小于 1 时按 1 处理
   * - ``book_content_width``
     - str
     - ``"46rem"``
     - 任何合法 CSS 长度
   * - ``book_header_buttons``
     - list[str]
     - ``download, fullscreen, source, edit, issue, repo``
     - 按序渲染；缺仓库坐标时只保留下载与全屏
   * - ``book_use_sidenotes``
     - bool
     - ``False``
     - 脚注转边注/ margin note；关闭时脚注保持原生
   * - ``book_footer_items``
     - list[str]
     - ``author, copyright, last-updated``
     - 预留

改过默认值的基座选项
--------------------

.. list-table::
   :header-rows: 1
   :widths: 30 24 46

   * - 选项
     - mystx 默认
     - 说明
   * - ``navbar_start``
     - 空
     - 基座默认 ``navbar-logo``
   * - ``navbar_center``
     - 空
     - 基座默认 ``navbar-nav``
   * - ``navbar_end``
     - 空
     - 基座默认 ``theme-switcher, navbar-icon-links``
   * - ``navbar_persistent``
     - 空
     - 基座默认 ``search-button-field``
   * - ``article_header_start``
     - 空
     - 去掉面包屑
   * - ``secondary_sidebar_items``
     - ``page-toc``
     - 去掉编辑/源码链接（后续移到页眉）
   * - ``nav_*`` 之外的基座选项
     - 继承
     - 见 pydata-sphinx-theme 文档

类型与默认值
------------

``theme.toml`` 中的值只能是字符串或数组。``book_nav_depth`` 一类整数选项在
构建开始时被转换；非法整数会记录一条 warning 并保留原值。

``book_nav_scope`` 的校验发生在 ``builder-inited``：非 ``book`` / ``section``
的取值会被改回 ``book``，避免模板层抛异常。

``book_use_sidenotes`` 只影响脚注：``{margin}`` 指令与相关样式始终可用，
因为它是块级排版能力，与脚注是否转边注无关。

版本耦合
--------

mystx 锁 ``pydata-sphinx-theme >= 0.24, < 0.25``。升级 minor 前请先跑文档站的
``-W`` 构建与快照测试；基座默认值与模板结构可能随 minor 变化。

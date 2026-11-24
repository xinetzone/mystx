导航
====

mystx 的侧栏仍然使用 pydata-sphinx-theme 的 toctree 算法，只改两个输入：
只改两个输入：``book_nav_scope`` （从哪一层开始）与 ``book_nav_depth`` （展开多深）。

两种阅读模型
------------

.. list-table::
   :header-rows: 1
   :widths: 22 40 38

   * - 取值
     - 行为
     - 适用
   * - ``book`` （默认）
     - 每页都渲染完整书目录（``startdepth=0``）
     - 教程、教材、连续阅读
   * - ``section``
     - 只渲染当前页所属顶层章节的子树（``startdepth=1``）
     - 多入口站点、手册

.. note::

   首页、搜索页、索引页没有上层章节。``section`` 模式下这些页面会自动回退为
   ``book``，避免 toctree 找不到祖先而报错。

顶层目录怎么写
--------------

``book`` 模式对根目录结构敏感：顶层 ``toctree`` 的条目就是“书”的篇章。

.. code-block:: rst

   .. toctree::
      :maxdepth: 2

      guide/index
      reference/index
      development/index

嵌套章节由各自页面的 ``toctree`` 展开：

.. code-block:: rst

   .. toctree::

      installation
      configuration
      navigation

展开深度
--------

- ``book_nav_depth`` 控制“初始展开到第几层”，默认 1：只显示顶层章节，其余折叠；
  当前页所在的那一章会自动展开，否则读者看不出自己在哪。
- ``navigation_depth`` （基座选项）控制“最多渲染到第几层”，默认 4。
- 两者关系：``book_nav_depth <= navigation_depth`` 时才会看到预期的展开效果。

当前页与高亮
------------

当前页标记由基座在构建期写入（``current`` / ``aria-current``），前端只负责滚动同步。
因此：

- 侧栏高亮错页时，先检查 toctree 结构，而不是改 CSS。
- 使用 ``dirhtml`` 构建时，基座不会缓存侧栏片段，高亮仍由构建期计算。

移动端
------

窄屏下主侧栏进入抽屉，由基座脚本负责搬移。mystx 没有改写这部分行为。

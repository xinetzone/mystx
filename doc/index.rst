mystx
=====

mystx 是面向书籍阅读的 Sphinx HTML 主题。它以 `pydata-sphinx-theme
<https://pydata-sphinx-theme.readthedocs.io/>`_ 为唯一基座，在其上实现三件书籍化的事：

- 左侧全书目录（而不是只显示当前章节子树）
- 单列阅读流 + 可调的正文宽度
- 页眉工具箱与脚注边注（后续版本）

.. list-table::
   :header-rows: 1
   :widths: 22 20 58

   * - 组成
     - 版本要求
     - 说明
   * - Python
     - >= 3.11
     - 与基座一致，不额外抬高
   * - Sphinx
     - >= 8.2, < 10
     - 与基座约束对齐
   * - pydata-sphinx-theme
     - >= 0.24, < 0.25
     - 唯一父主题，锁 minor

.. note::

   当前版本处于 P2 阶段：全书导航、navbar 中和、正文宽度、页眉工具箱已可用；
   边注尚未实现，相关选项已预留但不会产生效果。

.. toctree::
   :hidden:
   :maxdepth: 2

   guide/index
   reference/index
   development/index

.. toctree::
   :hidden:
   :maxdepth: 1

   changelog

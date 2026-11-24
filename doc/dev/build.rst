构建与发布
==========

构建后端为 ``scikit-build-core`` + ``setuptools-scm``，纯 Python，
``cmake = false``，不需要本机安装 CMake 或 Node。

本地构建
--------

.. code-block:: console

   python -m build --wheel --no-isolation

产物为 ``py3-none-any``，其中包含：

- ``mystx/theme/mystx/theme.toml``
- ``mystx/theme/mystx/*.html``
- ``mystx/theme/mystx/static/css/*.css``

版本号
------

版本来自 git tag，格式为 ``vX.Y.Z``：

- 首个正式 tag：``v0.0.1`` → 发行版版本 ``0.0.1``
- tag 之后的新提交：``0.0.2.devN+g<sha>``
- 无 git 元数据：``0.0.0.dev0``

CI 注意：``actions/checkout`` 需设置 ``fetch-depth: 0``，否则浅克隆看不到 tag，
版本会静默回退。

测试
----

.. code-block:: console

   pytest tests/test_nav.py tests/test_build.py

``test_build.py`` 会在临时目录生成最小站点，用 ``warningiserror=True`` 构建，
断言：全书树可见、当前页有 ``aria-current``、无 ``navbar-nav``、
``css/book.css`` 已注入、``section`` 模式只显示当前章节。

文档站构建
----------

.. code-block:: console

   sphinx-build -b html doc _build/html -W --keep-going

Read the Docs 使用 ``doc/conf.py`` 并开启 ``fail_on_warning``，因此新增文档必须
进入某个 ``toctree``，否则会红。

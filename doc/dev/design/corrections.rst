实施修正记录
============

4.13 两处收尾修正（第 8 条关单 + 窄屏边注）
-------------------------------------------

**第 8 条已补齐。** 从 ``dist/*.tar.gz`` 解包到空目录，用
``python -m build --wheel --no-isolation`` 重建：构建成功，产出
``py3-none-any`` wheel，14 个必需资源（3 个 CSS、\ ``book.js``\ 、5
个模板、5 个 Python 模块）全部在内。\ ``--no-isolation`` 不下载
任何构建依赖，等价于"断网自足"。剩下只有版本号一项：仓库里有
``v0.1.1``–``v0.3.8`` 共 13 个旧 tag，\ ``setuptools-scm`` 因此推出
``0.3.9.dev130+g7e4e203``\ ；打 ``v0.0.1`` 后才会是
``0.0.1``\ ，这一步需要人拍板。

**窄屏边注展开不再挤掉标点。** 原先展开态写
``display: block``\ ，导致引用点之后的
句号被推到独立一行，段落读起来断成两截（截图对比过：一张图上孤零零一个"。"）。
改成行内色块（\ ``display: inline`` +
``box-decoration-break: clone``\ ），段落流不再被
切开，跨行时左右边框也能正确复制。\ ``aside.margin``
这类块级留白不受影响，仍在窄屏 折回正文流。

4.14 收尾决定
-------------

暂不打 ``v0.0.1``\ ：版本号继续由 ``setuptools-scm`` 从旧 tag
推导（\ ``0.3.9.dev*``\ ）。
理由是首次发布不必绑在验收上；真要发版时只需
``git tag v0.0.1``\ ，代码不用改。

子模块指针已提交：\ ``xuanspace`` → ``0a39b9a``\ ，外层 ``SpecWeave`` →
``fb5d2234d``\ 。 顺手补一个 ``gitignore``
漏项：\ ``tests/chaos/src/mystx/_version.py`` 由构建生成却没被
忽略，导致子模块长期显示脏；规则改为 ``**/src/mystx/_version.py``\ 。

4.15 分区首页的大片空白
-----------------------

现象：\ ``guide/index.html`` 这类分区首页左侧有一条约 100px
的空条，右侧整块空白。

定位（实测 ``getBoundingClientRect``\ ，视口 1280）：\ ``.bd-content``
宽 949，正文容器宽 736（\ ``book_content_width`` 的 46rem 上限），基座
``.bd-content`` 是 ``justify-content: center``\ ，于是两侧各分到约 107px
空白。右侧那条空白本该站页内 目录，但分区首页只有
toctree、没有页内标题，\ ``display_toc`` 为假，基座整块不渲染
``.bd-sidebar-secondary``\ ，于是左右两处空白同时出现，看起来像排版坏了。

处置：页面结构决定布局类名（\ ``body_classes()``\ ），模板只输出。\ ``display_toc``
为假时 给 ``<body>`` 加 ``mystx-no-toc``\ ，CSS 在 ``>=960px``
把该类页面的 ``.bd-content`` 改成
``justify-content: flex-start``\ ，正文贴着侧栏起排；有目录的页面完全不变。

取舍：没有把限宽改成按视口伸缩。行宽上限是书籍阅读的核心约束，宁可留白也不拉长行。
也没用 ``:has()`` 选择器，避免老浏览器静默退化。

4.16 侧栏默认只展开顶层
-----------------------

原来 ``book_nav_depth = 3``\ ，PST 的 ``show_nav_level`` 会把
``li.toctree-l0..2`` 的 ``<details>`` 全部标
``open``\ ，于是每章的子目录一开始就摊开。

改成 ``1``\ ：只有 ``toctree-l0`` 会被强制展开，而真实层级从
``toctree-l1`` 起， 等价于不额外展开任何层级，只剩 PST 的
``_set_current_chain()`` 生效——当前页所在的
章节链自动打开，读者仍能看出自己在哪；其他章节一律折叠，点箭头才展开。

``doc/conf.py`` 里还写着
``book_nav_depth: 3``\ ，会盖掉主题默认值，同批删掉。
``show_nav_level``\ （基座选项）一并置 1：mystx 的侧栏不用它，留着 3
只会误导。

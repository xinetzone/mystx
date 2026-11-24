更新日志
========

0.0.1（未发布）
---------------

- 以 ``pydata-sphinx-theme`` 为唯一基座（``>=0.24,<0.25``）。
- 新增全书侧栏：``book_nav_scope`` / ``book_nav_depth``。
- 新增正文宽度选项 ``book_content_width`` （CSS 变量注入）。
- 默认清空 ``navbar_*`` 与面包屑，移除右栏的编辑/源码链接。
- 选项归一化与 ``book_nav_scope`` 校验；``section`` 模式在无祖先页面回退全书树。
- 页眉工具箱：下载、全屏、仓库、编辑、源码、issue（GitHub / GitLab / Bitbucket）。
- 打包：``scikit-build-core`` + ``setuptools-scm``，``py3-none-any``。

尚未实现
--------

- 脚注转边注与 ``margin`` 指令（P3）
- 内容页脚组件（P4）

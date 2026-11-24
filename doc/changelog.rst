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
- 边注：``book_use_sidenotes`` 把脚注搬到右侧留白，``{-}`` 前缀转为无编号
  margin note；新增 ``{margin}`` 块级指令；含边注的页面在宽屏自动让出页内目录。
  窄屏开关是普通复选框，可 Tab 到达、Space 展开，焦点框画在可见编号上。
- 内容页脚：``book_footer_items`` 支持 ``author`` / ``copyright`` /
  ``last-updated``；置空则回退基座页脚。
- Notebook 样式：``div.cell`` 的间距、长输出滚动、``tag_margin`` /
  ``tag_full-width`` 复用留白列；纯 CSS，不引入 myst-nb 依赖。
- MyST 兼容：``myst-parser>=5.2`` 下 Markdown 源文件可用全部主题能力（边注、
  ``{margin}``、全书侧栏）；主题自身仍不依赖 ``myst-parser``。
- 打包：``scikit-build-core`` + ``setuptools-scm``，``py3-none-any``。

尚未实现
--------

- 无（P0–P4 全部落地；后续为维护与基座升级）

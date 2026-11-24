---
type: Design
title: "mystx 新主题洞察方案：PST 基座 + SBT 三项能力"
description: "从零设计 mystx 主题：以 pydata-sphinx-theme 为唯一基座，只借鉴 sphinx-book-theme 的全书导航、页眉工具箱、边注三项能力；不继承既有配置与测试沙箱"
tags: [mystx, sphinx, theme, pydata-sphinx-theme, sphinx-book-theme, design, seven-concepts]
generated: { by: "main-agent/lobsterai", at: "2026-11-24T14:02:47+08:00" }
status: implementing
stale_after: 2027-05-24
sources:
  - id: bundle-pst
    resource: ../../../../awesome-okf-xs/doc/bundles/jishu/document/sphinx/pydata-sphinx-theme
    title: PST 知识包（88 事实 / 6 洞察 / 3 模式）
  - id: bundle-sbt
    resource: ../../../../awesome-okf-xs/doc/bundles/jishu/document/sphinx/sphinx-book-theme
    title: SBT 知识包（185 事实 / 7 洞察）
scope: 新主题的架构与首版范围；不含实现代码
---

# mystx 新主题洞察方案：PST 基座 + SBT 三项能力

> **结论先行**：这是一个**新主题**，不是旧配置的迁移。`inherit = pydata_sphinx_theme`，只带三样东西——全书侧栏、页眉工具箱、边注；选项用 PST 原生名 + 6 个 `book_*` 新键，不复制 SBT 的 30 个选项，不做兼容层，不引入配置加载器、字体管线、预设与扩展。自有代码目标 < 900 行。

> **实施进度**：P0（包骨架、基座切换、navbar 中和）与 P1（全书侧栏）已落地；P2（页眉工具箱）已完成。`pytest` 19 项通过，`doc/` 在 `-W` 下构建通过，wheel 为 `py3-none-any` 且包含主题资源。

> **范围声明**：`tests/chaos/` 属于测试沙箱，本方案不读取、不继承、不迁移其中任何模块或取值。

## 0. 决策摘要

| 决策 | 结论 |
|---|---|
| 基座 | `pydata-sphinx-theme`（唯一父主题） |
| SBT 角色 | 参考实现，代码级借鉴，不进依赖 |
| 首版能力 | 全书侧栏、页眉按钮、边注（+ 单列阅读 CSS） |
| 选项策略 | PST 原名 + `book_*` 新键；不设 SBT 别名 |
| 兼容层 | 不做（无历史配置需要兼容） |
| 构建后端 | `scikit-build-core` + `setuptools-scm`（`cmake=false`，纯 Python 不需要 CMake） |
| 依赖 | `sphinx>=8.2` + `pydata-sphinx-theme`；MyST/Notebook 由站点自行选择 |

## 1. 基线

| 项 | 取值 | 理由 |
|---|---|---|
| Python | `>=3.11` | 与 PST 要求一致，不额外抬高 |
| Sphinx | `>=8.2,<10` | 与 PST 的约束对齐 |
| 父主题 | `pydata-sphinx-theme>=0.24,<0.25` | 本机 3.14 环境解析到 0.24.0，已做 PoC 验证 |
| 构建后端 | `scikit-build-core>=0.11` + `setuptools-scm>=8` | 产物 `py3-none-any`；版本取自 git tag，无需手写 |
| 版本起点 | tag `v0.0.1` | `setuptools-scm` 去掉前缀后推导发行版版本 `0.0.1` |
| 打包内容 | `src/mystx` 全量（含 `theme/**` 资源） | `wheel.packages` 递归收集，非 `.py` 文件随包发布 |
| 自有代码 | `src/mystx/` 约 6 个模块 | 见 §4.6 |
| 文档构建 | `doc/` 新建 | 不复用任何既有站点结构 |

**不引入清单**（与 `tests/chaos/` 划清边界）：

| 类别 | 不引入的理由 |
|---|---|
| TOML 配置加载器 / presets | 主题默认值应写在 `theme.toml`，站点覆盖走 `html_theme_options`；再加一层配置源会让"取值从哪来"不可判定 |
| 字体注册管线 | PST 已提供字体变量；站点字体属于站点配置，不属于主题 |
| `myst_compat` 钩子 | 兼容层针对旧解析器行为；新主题直接对齐 myst-parser 5.x |
| 并行守卫 | PST 声明 `parallel_read_safe/write_safe`，主题无需重复 |
| 版本切换器封装 | PST 已有 `switcher` + `switcher.json`，不重写 |
| `ext/gallery`、GitHub 统计卡片 | 文档扩展与主题职责无关 |
| `tasks/` 文档任务 | 构建任务属于站点，不属于主题包 |

## 2. F｜公理识别

| # | 公理 | 对本方案的约束 |
|---|---|---|
| A1 | 主题是构建期应用，能力边界由事件决定 | 三项能力必须各自找到事件挂点，而不是只写 CSS |
| A2 | 布局 = 有序模板列表 + 空渲染剪枝 | 书籍布局靠"换组件 + 换顺序"，不重写骨架 |
| A3 | 配置是三层投影，类型在边界失真 | 新选项在 `theme.toml` 定默认值，模板用显式转换 |
| A4 | 阅读模型决定导航算法 | 单列 + 全书树是"书"的必需项 |
| A5 | 继承是契约：覆盖点越少，父版本越硬 | 覆盖 block 清单化，配快照测试 |
| A6 | 资产 = 源/产物分离 | 只交付 CSS 产物，不引入 Node 工具链 |

## 3. V｜假设攻击

| # | 假设 | 攻击 | 结论 |
|---|---|---|---|
| V1 | "从零写主题工作量很大" | PST 提供骨架、导航算法、双主题、搜索、a11y；自有部分只有 3 个模块 | **否**：目标 < 900 行 |
| V2 | "直接复制 SBT 组件最快" | SBT 组件引用 `theme_use_*`、`header_buttons`、repo 上下文；在 PST 下会空渲染 | **否**：按"数据协议"重写，不搬模板 |
| V3 | "沿用 SBT 选项名便于以后迁移" | 新主题没有历史配置；保留 SBT 名会制造伪兼容与双命名空间 | **否**：只用 PST 名 + `book_*` |
| V4 | "边注可以最后再加" | 边注是 doctree 变换，晚加会改动模板与 CSS 契约 | **否**：P3 前先定 transform 优先级与节点结构 |
| V5 | "PST 用 main 最新最省事" | 默认值与模板结构随 minor 变化 | **否**：锁 minor + 快照 |
| V6 | "主题要自带 MyST/Notebook 支持" | 解析与执行属于扩展；主题只负责 HTML 结构 | **否**：只写 Notebook 的样式类，不接管扩展 |

## 4. I｜方案

### 4.1 架构

```text
mystx（单继承）
└── inherit = pydata_sphinx_theme
    ├── 复用：事件管线 / 三套目录算法 / 双主题 / 搜索 / a11y / Bootstrap 资产
    └── 自有（book layer）
        ├── navigation  侧栏全书树（只改 startdepth 与深度参数）
        ├── buttons     页眉工具箱（数据 → 宏）
        └── sidenotes   脚注转边注 + margin 指令
```

只允许一层继承。**禁止**把 SBT 的 `layout.html` 复制进来，也禁止"继承 PST 再 monkey-patch SBT"。

### 4.2 首版能力（3 + 1）

| 能力 | 来源 | 实现层 | 首版 |
|---|---|---|---|
| 全书侧栏树 | SBT 的 `startdepth=0` 用法 | 组件 + 参数 | 是 |
| 页眉工具箱 | SBT 的按钮数据协议 | Python 数据 + 宏 | 是（5 个基础按钮） |
| 边注 / margin | SBT 的 transform + node + 指令 | Python + CSS | 是 |
| 单列阅读宽度 + 右留白 | SBT 的 SCSS 思路 | CSS | 是 |
| 启动按钮（Binder/Colab/Thebe） | SBT | Python | 否，二期 |

### 4.3 选项设计

**复用 PST 原生选项**（不重命名）：`navbar_*`、`secondary_sidebar_items`、`article_header_start/end`、`footer_start/end`、`announcement`、`icon_links`、`switcher`、`pygments_*`。

**新增 6 个 `book_*` 选项**：

| 选项 | 类型 | 默认 | 作用 |
|---|---|---|---|
| `book_nav_scope` | str：`book` / `section` | `"book"` | 侧栏渲染全书树还是当前章节子树 |
| `book_nav_depth` | int | `3` | 全书树初始展开层数 |
| `book_header_buttons` | list[str] | `["download", "fullscreen", "source", "edit", "issue", "repo"]` | 页眉按钮及顺序 |
| `book_use_sidenotes` | bool | `False` | 脚注转边注总开关 |
| `book_content_width` | str | `"46rem"` | 正文最大宽度（CSS 变量） |
| `book_footer_items` | list[str] | `["author", "copyright", "last-updated"]` | 内容页脚组件 |

设计原则：**一个能力一个开关**，布尔与列表都显式转换；不提供 `use_*_button` 六个布尔，改为一个有序列表（顺序即渲染顺序，删除即关闭）。

### 4.4 模板与组件

| 文件 | 职责 | 目标行数 |
|---|---|---|
| `theme/mystx/theme.toml` | `inherit`、样式表、6 个选项默认值 | ~40 |
| `theme/mystx/layout.html` | 只覆盖必要 block（导航区、正文容器） | < 60 |
| `components/book-nav.html` | 调 `generate_toctree_html(startdepth=0)` | ~25 |
| `components/header-buttons.html` | 遍历 `header_buttons`，按 `type` 选宏 | ~30 |
| `components/page-toc.html` | 页内目录标题与层级 | ~15 |
| `components/footer-items.html` | 内容页脚列表 | ~15 |
| `macros/buttons.html` | `link` / `javascript` / `group` 三个宏 | ~40 |

### 4.5 Python 模块

| 模块 | 职责 | 关键点 |
|---|---|---|
| `book/navigation.py` | 计算侧栏参数 | 不重写 toctree 算法，只传 `startdepth` 与深度 |
| `book/buttons.py` | 生成按钮字典列表 | URL 规则纯函数、可单测；无仓库信息时返回空列表 |
| `book/sidenotes.py` | transform + node + 指令 | 优先级 1，仅 `html` 格式；关闭时不注册 |

> **落地修正（P3）**：节点、指令与变换一律在 `setup()` 注册，开关在 `run()` 内短路。
> 理由有两条：`{margin}` 是块级能力，不该因为脚注开关被禁用；资产注册若依赖
> `builder-inited` 时的选项，会让"关→开"的增量构建残留缺样式页面。
| `__init__.py` | `setup()` 注册主题与能力 | 返回 `parallel_read_safe/write_safe` |

### 4.6 目录结构

```text
mystx/
├── pyproject.toml
├── src/mystx/
│   ├── __init__.py
│   ├── book/navigation.py
│   ├── book/buttons.py
│   ├── book/sidenotes.py
│   └── theme/mystx/
│       ├── theme.toml
│       ├── layout.html
│       ├── components/*.html
│       ├── macros/buttons.html
│       └── static/css/{book,sidenotes,mystx}.css
├── doc/conf.py + index.md
├── tests/{test_buttons.py,test_build.py,test_sidenotes.py}
└── design/（本文件）
```

### 4.7 阶段计划

| 阶段 | 内容 | 验收 | 预估 |
|---|---|---|---|
| P0 | 包骨架、`theme.toml`、`layout.html`、`doc/` 最小站点 | 构建通过；页面无双重导航 | 0.5 天 |
| P1 | 全书侧栏（`book_nav_scope/book_nav_depth`） | 三层目录展开正确；`dirhtml` 下高亮不串页 | 0.5 天 |
| P2 | 页眉按钮（5 个基础 + 全屏） | URL 单测；无仓库信息时区段消失 | 1 天 |
| P3 | 边注 / margin | 行内、块级、嵌套三类用例；开关关闭后与原生脚注一致 | 1.5 天 |
| P4 | 单列宽度、页脚组件、Notebook 样式 | 4 类页面快照稳定 | 1 天 |

### 4.8 构建与打包

`pyproject.toml` 的关键段（纯 Python 主题，禁用 CMake）：

```toml
[build-system]
requires = ["scikit-build-core>=0.11", "setuptools-scm>=8"]
build-backend = "scikit_build_core.build"

[project]
name = "mystx"
dynamic = ["version"]
requires-python = ">=3.11"
dependencies = ["sphinx>=8.2,<10", "pydata-sphinx-theme>=0.24,<0.25"]

[project.entry-points."sphinx.html_themes"]
mystx = "mystx"

[tool.scikit-build]
minimum-version = "0.11"
wheel.cmake = false
sdist.cmake = false
sdist.include = ["src/mystx/theme/**", "README.md", "LICENSE"]

[tool.scikit-build.wheel]
packages = ["src/mystx"]

[tool.setuptools_scm]
version_file = "src/mystx/_version.py"
write_to = "src/mystx/_version.py"
```

| 要点 | 说明 |
|---|---|
| 版本号 | `setuptools-scm` 由 git tag 推导；首个 tag 为 `v0.0.1` → 发行版 `0.0.1`；`version_file` 供 `__init__` 读取；无 git 元数据时回退 `0.0.0.dev0` |
| CI 取版本 | checkout 需 `fetch-depth: 0`；浅克隆看不到 tag，版本会静默回退为 dev0 |
| 无 CMake | `wheel.cmake=false` 与 `sdist.cmake=false` 两处显式关闭，构建不要求 cmake/ninja |
| 主题资源 | `wheel.packages` 递归收集 `src/mystx`，`theme/` 下的 `.html` / `.toml` / `.css` 作为包数据入 wheel，无需 `MANIFEST.in` |
| sdist | `sdist.include` 显式列出 `theme/**`，防止源码包丢模板 |
| 不入包 | `doc/`、`design/`、`tests/` 不进入 wheel |

### 4.9 测试策略

1. 三个 fixture 站点：`basic`（无仓库）、`book`（多层目录）、`notebook`（myst-nb 输出）。
2. 构建断言：`builder-inited` 后无 warning；关键 HTML 片段（`nav.bd-sidenav`、按钮组、边注 label）。
3. 纯函数单测：按钮 URL、选项归一化。
4. 可选：Playwright + axe 冒烟（进 CI 前先跑本地）。

### 4.10 PoC 验证记录（已完成）

环境：CPython 3.14.0（uv 管理）、Sphinx 9.2.0、pydata-sphinx-theme 0.24.0。
做法：在临时目录建一个子主题（`inherit = pydata_sphinx_theme`，`sidebars = book-nav.html`，`book-nav.html` 调用 `generate_toctree_html(startdepth=0)`，并清空 `navbar_*`），用 `-W --keep-going` 构建一个 4 页小站。

| 验证项 | 结果 | 证据 |
|---|---|---|
| PST 子主题在 py3.14 上可构建 | 通过 | `build succeeded`，无 warning |
| `generate_toctree_html` 支持 `startdepth=0` | 通过 | 函数签名 `(kind, startdepth=1, show_nav_level=1, **kwargs)` |
| 每个页面都渲染全书树 | 通过 | 首页、章节页、子页均含 Guide / Setup / Deep / API 四项 |
| 当前页高亮 | 通过 | 每页恰好 1 个 `aria-current` |
| 清空 `navbar_*` 可去除头部导航 | 通过 | 输出中无 `navbar-nav` |
| 模板回退到父主题 | 通过 | 子主题只需覆盖 `book-nav.html`，其余模板由 PST 提供 |

结论：方案中 P0 + P1 的核心机制（换基座、清空 navbar、全书树）已在 py3.14 上验证可行；剩余风险集中在样式与边注，不在架构。

### 4.11 落地进度

| 阶段 | 状态 | 证据 |
|---|---|---|
| P0 骨架 + 基座切换 | 已完成 | `-W` 构建 0 warning；`navbar-*` 区为空 |
| P1 全书侧栏 + 正文宽度 | 已完成 | 27 项测试；`book/section` 两种 scope |
| P2 页眉工具箱 | 已完成 | 6 个按钮；缺坐标降级为下载 + 全屏 |
| P3 边注 + `{margin}` | 已完成 | 8 项边注测试；宽屏实测 1600px 见边注，1200px 收为可展开 |
| P4 页脚组件 + Notebook 样式 | 已完成 | 7 项页脚测试；页脚接管与回退双路径；Notebook 仅 CSS |

P3 与方案的三处偏差（均为实测倒逼）：

1. **变换常驻、开关短路**：见 4.5 的落地修正。
2. **边注布局改为按页让栏**：PST 的右栏被页内目录占用，浮动边注会压在目录下面。
   实测后改成"含边注的页面才隐藏右侧目录栏"，`<body>` 加 `mystx-has-margin`，
   纯正文页面完全不变；断点定在 1400px，低于此宽度边注折叠为点击展开。
3. **副本类名语义修正**：上游把 `d-n` 追加到"原地保留的那份"，复制时无条件加类，
   导致没有容器的普通段落也被标记为窄屏副本、宽屏整段消失。mystx 只在真正把正文
   提到容器外时才加 `d-n`。

P4 的两处收缩：

1. **页脚做"接管或回退"，不做叠加**：`book_footer_items` 非空时用自己的
   `book-footer.html`，置空才渲染基座 `sections/footer.html`。两套页脚同时出现是
   SBT 迁移期最常见的错位来源，直接二选一。
2. **Notebook 只写 CSS，不引入 myst-nb**：按 `div.cell` / `tag_margin` /
   `tag_full-width` 这些稳定类名写样式；装了 myst-nb 才生效，没装时零成本。

### 4.12 验收核对（对照 §6）

| # | 标准 | 结果 | 证据 |
|---|---|---|---|
| 1 | `doc/` 在 `fail_on_warning` 下 0 新增 warning | 通过 | `-W` 构建 `build succeeded`，14 页 |
| 2 | 直接依赖只有 `sphinx` + `pydata-sphinx-theme` | 通过 | `pyproject.toml` 的 `dependencies` 仅两项 |
| 3 | 自有 Python < 900 行；模板覆盖 < 60 行 | 通过 | Python 598 行；模板 52 行（页脚 7 / 页眉 13 / 侧栏 9 / layout 23） |
| 4 | 6 个 `book_*` 选项有默认值、类型转换与文档 | 通过 | `theme.toml` 默认值 + `normalize_theme_options` + options 页逐项说明 |
| 5 | 关闭 `book_use_sidenotes` 时与 Pure PST 输出一致 | 通过 | `test_switch_off_keeps_plain_footnotes`（无 `margin-toggle`、有 `footnote-list`） |
| 6 | 无 Node 构建步骤 | 通过 | 仓库无 `package.json` / 打包脚本，静态资源直接入库 |
| 7 | `python -m build` 产 `py3-none-any`，安装后资源就位 | 通过 | wheel 解包到隔离目录后构建站点，7 项断言全过（主题 CSS、边注、margin 块、页脚、页眉） |
| 8 | sdist 可解包离线构建；版本与 tag 一致 | 部分 | sdist 已排除测试沙箱（`tests/chaos`）与 `doc/_build`；未做断网重建；版本仍由仓库旧 tag 推导为 `0.3.9.dev*`，需打 `v0.0.1` 才符合 |

为满足第 3 条做的一次重构：页眉按钮的"链接还是脚本"、下载路径、图标全部下沉到
`book/buttons.py`（`href` / `download` / `javascript`），页脚前缀标签改为模板内
一张小字典。模板从 74 行降到 52 行，且判断逻辑从模板移回可单测的 Python。

同时修掉一个打包隐患：`sdist` 之前把 `tests/chaos/` 整个打进去（含第二份
`theme.toml`），文件数从 144 降到 76；`pyproject` 的 `norecursedirs` 也排除
`tests/chaos` 与 `tests/unit`，裸跑 `pytest` 只收主题的 34 项测试。

### 4.13 两处收尾修正（第 8 条关单 + 窄屏边注）

**第 8 条已补齐。** 从 `dist/*.tar.gz` 解包到空目录，用 `python -m build --wheel
--no-isolation` 重建：构建成功，产出 `py3-none-any` wheel，14 个必需资源（3 个
CSS、`book.js`、5 个模板、5 个 Python 模块）全部在内。`--no-isolation` 不下载
任何构建依赖，等价于"断网自足"。剩下只有版本号一项：仓库里有 `v0.1.1`–`v0.3.8`
共 13 个旧 tag，`setuptools-scm` 因此推出 `0.3.9.dev130+g7e4e203`；打 `v0.0.1`
后才会是 `0.0.1`，这一步需要人拍板。

**窄屏边注展开不再挤掉标点。** 原先展开态写 `display: block`，导致引用点之后的
句号被推到独立一行，段落读起来断成两截（截图对比过：一张图上孤零零一个"。"）。
改成行内色块（`display: inline` + `box-decoration-break: clone`），段落流不再被
切开，跨行时左右边框也能正确复制。`aside.margin` 这类块级留白不受影响，仍在窄屏
折回正文流。

### 4.14 收尾决定

暂不打 `v0.0.1`：版本号继续由 `setuptools-scm` 从旧 tag 推导（`0.3.9.dev*`）。
理由是首次发布不必绑在验收上；真要发版时只需 `git tag v0.0.1`，代码不用改。

子模块指针已提交：`xuanspace` → `0a39b9a`，外层 `SpecWeave` → `fb5d2234d`。
顺手补一个 `gitignore` 漏项：`tests/chaos/src/mystx/_version.py` 由构建生成却没被
忽略，导致子模块长期显示脏；规则改为 `**/src/mystx/_version.py`。

### 4.15 分区首页的大片空白

现象：`guide/index.html` 这类分区首页左侧有一条约 100px 的空条，右侧整块空白。

定位（实测 `getBoundingClientRect`，视口 1280）：`.bd-content` 宽 949，正文容器宽
736（`book_content_width` 的 46rem 上限），基座 `.bd-content` 是
`justify-content: center`，于是两侧各分到约 107px 空白。右侧那条空白本该站页内
目录，但分区首页只有 toctree、没有页内标题，`display_toc` 为假，基座整块不渲染
`.bd-sidebar-secondary`，于是左右两处空白同时出现，看起来像排版坏了。

处置：页面结构决定布局类名（`body_classes()`），模板只输出。`display_toc` 为假时
给 `<body>` 加 `mystx-no-toc`，CSS 在 `>=960px` 把该类页面的 `.bd-content` 改成
`justify-content: flex-start`，正文贴着侧栏起排；有目录的页面完全不变。

取舍：没有把限宽改成按视口伸缩。行宽上限是书籍阅读的核心约束，宁可留白也不拉长行。
也没用 `:has()` 选择器，避免老浏览器静默退化。

## 5. E｜可复用模式

### P-01 基座与体验层分离

基座只放"所有站点都需要"的能力；领域体验（书籍阅读）作为本包模块。判据：某项能力只对一类站点有价值 → 体验层。

### P-02 能力移植四件套

移植上游能力时拆成 **数据协议 / 模板 / Python 变换 / 样式** 四件，只取所需，并记录来源与许可。反模式：为一个功能依赖整个上游主题。

## 6. 验收标准

1. `doc/` 在 `fail_on_warning` 下构建通过，新增 warning = 0。
2. 依赖树只有 `sphinx` + `pydata-sphinx-theme` 两个直接依赖。
3. 自有 Python 代码 < 900 行；模板覆盖 < 60 行。
4. 6 个 `book_*` 选项均有默认值、类型转换与文档示例。
5. 关闭 `book_use_sidenotes` 时，输出与未安装本主题的 PST 站点一致（除品牌样式）。
6. 无 Node 构建步骤。
7. `python -m build` 产出 `py3-none-any` wheel；安装后 `theme/mystx/theme.toml` 与全部静态资源就位。
8. sdist 解包后可离线构建；版本号与 git tag 一致（首个 tag `v0.0.1` → `0.0.1`），无 tag 时为 `0.0.0.dev0`。

## 7. 风险

| 风险 | 缓解 |
|---|---|
| 双重导航（PST 默认 navbar + 全书侧栏） | `theme.toml` 显式清空 navbar 区，P0 快照验收 |
| 边注在 myst-nb 输出中错位 | 三类用例 + 开关回退 |
| PST minor 升级破坏模板契约 | 锁 minor + 4 类快照 |
| 借鉴代码的许可 | 文件头保留 BSD-3 归属，仓库加 NOTICE |
| 范围蔓延（又想做扩展） | 守住"三模块"；扩展需求另开包 |

## 8. 待确认

| # | 问题 | 建议 |
|---|---|---|
| Q1 | Python 下限取 3.11 还是 3.13 | 3.11，与 PST 对齐 |
| Q2 | 首版是否需要启动按钮 | 否，二期 |
| Q3 | 是否提供 `book_nav_scope="section"` 兼容站点式导航 | 提供；默认 `book` |

> 首个版本 tag 已定为 `v0.0.1`（§1 版本起点、§4.8 构建规则、§6 验收同步）。

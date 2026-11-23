# mystx 项目变更日志

本文档记录 mystx 项目的所有重要变更。

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

## [Unreleased]

### 变更

- **配置层：`config.py` 与 `configs.py` 合并为 `mystx.config` 包。** 两者文件名仅差一个 `s`，但职责分属不同生效时点：原 `configs.py` 服务构建期的 conf.py 字典组装，原 `config.py` 服务运行期 `config-inited` 对 Sphinx `Config` 的注入。现按该正交轴拆为 `mystx.config.defaults`（静态默认与 `build_base_config`）与 `mystx.config.runtime`（`ConfigManager`、`config_inited_handler` 等），由包 `__init__` 统一导出；`mystx.config.*` 的既有导入路径不变。
- **默认值：书系主题 `navbar_persistent` 改为单一权威源。** `BOOK_THEME_OPTION_DEFAULTS` 取值改为引用 `themes.DEFAULT_BOOK_THEME_OPTIONS`，消除同一默认值两处副本，避免 preset 路径与运行期注入路径分叉后重现双搜索框回归。
- **主题默认值：`theme.toml` 与 `themes.DEFAULT_BOOK_THEME_OPTIONS` 对齐并加机检守卫。** 二者对 13 个同名键各自声明，其中 8 个已分歧（`use_repository_button`/`use_source_button`/`use_issues_button`、`show_navbar_depth`、`max_navbar_depth`、`toc_title`、`navbar_persistent`），导致纯主题接入与 preset 接入呈现不同行为。现将 `theme.toml` 对齐到 Python 侧意图值，并新增 `tests/unit/test_theme_toml_consistency.py`，把"同名键取值必须一致"固化为机检门禁。
- **预设：删除 `minimal_myst` 的 `_MINIMAL_KEY_DEFAULTS` 整表副本。** 其 5 个键与 `presets._shared._COMMON_KEY_DEFAULTS` 逐字相同，且后者本就先于前者叠加，属纯冗余。
- **主题名单：`BOOK_THEME_NAMES` 收敛为 `themes.py` 单一权威源。** 原在 `DEFAULT_THEME_PRIORITY`、`resolve_theme_options` 字面量与 `config.defaults` 三处各写一份。
- **sitemap 环境判定：抽取 `utils.sitemap_enabled_by_env()`。** `extensions._sitemap_conditional` 与 `config.defaults._resolve_html_baseurl` 改为共用同一分支实现，避免 CI/RTD 判定两处漂移。
- **文档站：从 `doc/conf.py` 萃取五个可复用单元到包内。** 原实现把跨项目通用的逻辑内联在单项目配置文件中，其他文档站只能复制：
  - 新增 `mystx.parallel`：中心化并行安全覆写表 + `env-before-read-docs` fail-fast 守卫。覆写表按扩展名批量声明 `parallel_{read,write}_safe`，未加载的扩展名静默跳过（一张表可跨项目复用）；守卫仅在调用方显式要求并行（`-j` / `$SPHINX_BUILD_JOBS`）时触发，并列出阻塞扩展名。
  - 新增 `mystx.myst_docs`：把 `myst_parser._docs` 的七个文档工具指令、两个后置变换与 `myst` 词法器收拢为 `register_docs_directives()`；示例指令的三个 CSS 类名由 `example_prefix` 参数化（默认 `myst-example`，与原 `local.css` 契约一致）。缺失 `myst-parser>=5.1` 时抛出带安装提示的 `ImportError`。
  - 新增 `mystx.fonts`：`configure_optional_matplotlib_fonts()` 把「字体包 / 字体目录 / 调用异常」三重守卫与静默降级收拢，返回是否生效，绝不抛出。
  - `mystx.utils.resolve_release()`：版本回退链「分发包元数据 → 环境变量 → 兜底值」，替代 `conf.py` 内联 try-except。
  - 新增 `mystx.ext.gallery`：`gallery-grid` 指令由 `doc/_ext/` 迁入包内（旧副本 `doc/_ext/gallery_directive.py` 已删除），下游无需再把 `doc/` 插入 `sys.path`；同时修复参数形式（YAML 文件路径不存在时）返回 `None` 导致指令异常的问题，改为返回提示段落并记 warning。
  - **依赖：`pyyaml>=6.0` 显式声明。** 迁入的 `mystx.ext.gallery` 在模块顶层解析 YAML 画廊数据，此前仅依赖传递安装；现同时加入 `[project.optional-dependencies].doc` 与 `[dependency-groups].doc` 两处清单，避免干净环境下启用该扩展即报 `ModuleNotFoundError`。
- **配置：新增 `DEFAULT_SITE_CONFIG`。** 收纳与项目身份无关的文档站通用键（`graphviz_output_format`、`inheritance_graph_attrs`、`sitemap_locales`、`tippy_rtd_urls` 与三条通用 `nitpick_ignore`）；**不**并入 `build_base_config`，由调用方显式取用，避免改变既有 preset 行为。
- **`doc/conf.py` 改为消费上述包内能力。** MyST 文档工具指令注册、并行覆写与守卫、字体增强、版本解析、gallery 扩展名均由包内提供；`invoke.Collection` 这一项目侧豁免项在 `DEFAULT_SITE_CONFIG` 基础上单独追加。同时移除了「mystx 不可导入」的降级分支——该分支不可达（同文件末尾无条件追加的 `mystx.ext.github_readme_stats` 与 autoapi 源目录都依赖包本身），保留它只会在 `conf.py` 内留下 `DEFAULT_SITE_CONFIG` 的第二份字面量，重现本仓反复修复的「双源漂移」缺陷。

### 修复

- **扩展：`github-pinned-repo` 的 `:link:` 与图片地址统一经 HTML 转义。** 原实现以 f-string 直接拼接 `<a href>`/`<img src>`，含 `"`、`<`、`&` 的链接可破坏标签结构。现统一经 `BaseGitHubCardDirective.create_image_node(..., link=...)` 生成，`link`、`url`、`alt` 均走 `html.escape`；无 `link` 时输出与旧实现一致。
- **文档：README 配置示例拼写修正。** Python 代码块内 `static_path` 改为 `html_static_path`，`"home_page_in_toc": false` 改为 `False`，避免照抄示例即报 `NameError` 或配置不生效。
- **脚本：`invoke doc.tree` 子目录重复打印与 `doc.browse` 启动顺序。** `tree` 原对同一子目录打印两次（枚举一次、递归一次），现仅由递归打印；`browse` 改为先启动 HTTP 服务器再打开浏览器，避免浏览器先于服务就绪。
- **任务 CLI：Sphinx 可执行命令统一解析。** 新增 `mystx.tasks.doc._core._sphinx_build_cmd()`，`build`、`doctest`、`-M` 目标三个入口共用 `$SPHINXBUILD`（缺省 `sphinx-build`），消除 `build`/`doctest` 两处硬编码字面量。
- **任务 CLI：`doc.clean`（builder 模式）增加构建根边界。** target 不在解析出的 builddir 内时拒绝删除并给出提示；空父目录回收不再越过构建根，避免误删项目目录。
- **配置：`use_thebe` 改为「先装配、后配置」。** 先 `setup_extension("sphinx_thebe")`，成功后再写 `launch_buttons.thebe=True`；装配失败时不再留下「按钮已开启但功能缺失」的状态。
- **打包：声明运行期依赖。** `dependencies` 由空改为 `sphinx>=8.0`、`sphinx-book-theme>=1.1`（`theme.toml` 的 `inherit` 必需），使干净环境 `pip install` 后 `import mystx` 即可用；`[project.optional-dependencies].doc` 继续承载文档构建增量。
- **扩展装配：恢复 `sphinxcontrib.mermaid`。** 与 `myst_fence_as_directive = ["mermaid"]` 配对，消除围栏指令的死映射（原注释「不在依赖中」已过时）；`has_module` 守卫保证未安装时静默跳过。新增契约测试防回归。

### 文档

- **清理 `doc/_ext/` 的上游复制件。** 删除 `component_directive.py`（pydata-sphinx-theme 的 `component-list` 指令复制件）：自 6a6993a 随文档目录迁移引入后从未在 `extensions` 中注册，`doc/` 下无任何 `component-list` 引用，且硬编码的 `src/pydata_sphinx_theme/theme/pydata_sphinx_theme/components` 在本仓并不存在（实测为 `False`），一旦启用即抛 `FileNotFoundError`。删除前记录 SHA-256 `AF8A7DBD…856CA2`。
- **`SW_MYST_COMPAT_*` 环境变量别名的移除版本明确为 `mystx>=0.7`。** 新规范前缀为 `MYSTX_MYST_COMPAT_*`；命中旧前缀时记录 info 级弃用提示，0.7 起移除该别名。

### 测试

- **补齐扩展与文档任务的回归用例。** 新增 `tests/unit/test_github_readme_stats.py`（HTML 转义、URL 拼装、缺参报错）以及 `tree`、`clean`、`browse`、`-M` 包装共 12 条用例；`tasks/doc/builder.py` 覆盖率 98%，`github_readme_stats` 的 `base.py` 与 `pinned_repo.py` 均达 100%。
- **`browse` 补充端到端集成用例。** 真实拉起 `http.server` 并回读页面内容，另覆盖端口占用时的自增选择。
- **mermaid 补充端到端构建用例。** 经 `build_minimal_myst_config` 装配 `sphinxcontrib.mermaid`，断言围栏被转换为 `mermaid` 指令节点并渲染出容器；构建在子进程中隔离执行，避免同进程多次 `Sphinx()` 的注册表污染。
- **萃取层机检门禁。** 新增 `test_parallel.py`（覆写/跳过/守卫三种触发条件）、`test_myst_docs.py`（类名派生、注册顺序、可选开关、缺依赖报错）、`test_fonts.py`（缺失、目录不存在、成功转发、后端抛错）、`test_ext_gallery.py` 与 `test_conf_py.py`（conf.py 确实消费包内能力，防止又长回内联副本）；`test_utils.py` 补齐 `resolve_release` 的四条回退链用例。

### 破坏性变更

- `mystx.configs` 模块移除：`DEFAULT_MYST_CONFIG`、`DEFAULT_BUILD_CONFIG`、`DEFAULT_EXT_CONFIG`、`DEFAULT_HTML_CONFIG`、`build_base_config` 请改从 `mystx.config` 导入；顶层 `mystx` 的导出保持不变。

## [v0.3.8] - 2026-10-15

### 修复

- **主题：消除顶栏与主侧边栏重复的搜索按钮。** pydata-sphinx-theme 0.16 起在 `builder-inited` 阶段为未声明 `navbar_persistent` 的项目自动注入 `["search-button-field"]`，与书系主题主侧边栏内置的搜索按钮叠加，导致页面出现两个外观相同的搜索按钮。现于 `config-inited`（早于 pydata 的注入时机）以 `setdefault` 语义为书系主题补齐 `navbar_persistent=[]`：用户在 `conf.py` 或 `_config.toml` 中的显式声明一律优先，非书系主题不受影响；侧边栏搜索按钮与搜索对话框（Ctrl+K）保持正常（809c8d8）。
- **CI：修复 Read the Docs 文档构建。** 旧配置使用的 ubuntu-26.04 + `mambaforge-latest` 工具链在 RtD 新镜像上失效（`asdf install` 阶段 `EnvironmentLocationNotFound: conda/latest`，构建十余秒即失败，从未进入文档编译阶段）。鉴于项目无真实 conda 依赖（`dev-environment.yml` 实质仅 pip 安装 `.[docs]`），改为 RtD 推荐组合：`ubuntu-24.04` + CPython `3.14`（满足 `requires-python>=3.14`），删除 conda 段，pip extras 由 `[docs, dev]` 收敛为 `[docs]`；`dev-environment.yml` 保留供本地 conda 用户使用。修复已由 latest 构建 #35085492 与 stable 构建 #35154370 验证通过（0b0b204）。

### 测试

- 新增 5 个单元测试锁定 `navbar_persistent` 注入语义（缺失时注入、显式声明保留、空列表、非书系主题不干预）。

[v0.3.8]: https://github.com/xinetzone/mystx/compare/v0.3.7...v0.3.8

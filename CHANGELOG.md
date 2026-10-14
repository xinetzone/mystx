# mystx 项目变更日志

本文档记录 mystx 项目的所有重要变更。

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

## [v0.3.8] - 2026-10-15

### 修复

- **主题：消除顶栏与主侧边栏重复的搜索按钮。** pydata-sphinx-theme 0.16 起在 `builder-inited` 阶段为未声明 `navbar_persistent` 的项目自动注入 `["search-button-field"]`，与书系主题主侧边栏内置的搜索按钮叠加，导致页面出现两个外观相同的搜索按钮。现于 `config-inited`（早于 pydata 的注入时机）以 `setdefault` 语义为书系主题补齐 `navbar_persistent=[]`：用户在 `conf.py` 或 `_config.toml` 中的显式声明一律优先，非书系主题不受影响；侧边栏搜索按钮与搜索对话框（Ctrl+K）保持正常（809c8d8）。
- **CI：修复 Read the Docs 文档构建。** 旧配置使用的 ubuntu-26.04 + `mambaforge-latest` 工具链在 RtD 新镜像上失效（`asdf install` 阶段 `EnvironmentLocationNotFound: conda/latest`，构建十余秒即失败，从未进入文档编译阶段）。鉴于项目无真实 conda 依赖（`dev-environment.yml` 实质仅 pip 安装 `.[docs]`），改为 RtD 推荐组合：`ubuntu-24.04` + CPython `3.14`（满足 `requires-python>=3.14`），删除 conda 段，pip extras 由 `[docs, dev]` 收敛为 `[docs]`；`dev-environment.yml` 保留供本地 conda 用户使用。修复已由 latest 构建 #35085492 与 stable 构建 #35154370 验证通过（0b0b204）。

### 测试

- 新增 5 个单元测试锁定 `navbar_persistent` 注入语义（缺失时注入、显式声明保留、空列表、非书系主题不干预）。

[v0.3.8]: https://github.com/xinetzone/mystx/compare/v0.3.7...v0.3.8

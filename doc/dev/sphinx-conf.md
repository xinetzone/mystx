# Sphinx conf.py 机制与可复用接口

> 本文是对上游 Sphinx 源码中 **配置系统（conf.py）** 的源码研究，面向
> `mystx.presets` 的配置层设计。按七概念方法论「知识沉淀」链路执行：
> R（事实）→ I（洞察）→ E（萃取），V 与 C 按需未执行。
>
> 结论先行：Sphinx 的配置系统本质是**「声明四元组 + 三源惰性合并 + 分类失效」**；
> mystx 预设已实现「装配与钩子分离」与声明单源，缺口在**取值类型断言、失效档位的实际消费**两项。

## 研究范围与溯源

| 项         | 取值                                               |
| --------- | ------------------------------------------------ |
| 上游源码      | `notebook/libs/sphinx-doc/sphinx/sphinx`         |
| Sphinx 版本 | 9.3.0（开发版，`version_info = (9, 3, 0, 'beta', 0)`） |
| 上游提交      | `035a07c32`（2026-10-30）                          |
| 下游消费者     | `mystx` HEAD `b39da5f`（2026-11-24）               |
| 研究日期      | 2026-11-24                                       |

下文证据一律写作 `文件:起止行`，行号对应该提交；不提供可点击的本地路径，
以免文档站读者拿到失效链接。

## R｜事实门（G1：24 条）

| #  | 客观事实                                                                                                                                         | 证据                                                                                                                              |
| -- | -------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| 1  | 配置文件名常量为 `CONFIG_FILENAME = 'conf.py'`；rebuild 取值域为 `''/'env'/'epub'/'gettext'/'html'/'applehelp'/'devhelp'`                                 | `sphinx/config.py:28-40`                                                                                                        |
| 2  | 配置寄存器条目是 `ConfigValue(name, value, rebuild)` 三元组（NamedTuple）                                                                                 | `sphinx/config.py:44-48`                                                                                                        |
| 3  | `ENUM` 提供候选集校验，`match()` 同时支持标量与序列入参                                                                                                         | `sphinx/config.py:75-91`                                                                                                        |
| 4  | `_Opt` 以 `__slots__` 加冻结的 `__setattr__`/`__delattr__` 实现不可变，并提供 `__hash__`/`__eq__`/`__lt__`/pickle 支持                                       | `sphinx/config.py:97-193`                                                                                                       |
| 5  | `_Opt.__repr__` 中 `valid_types` 位置实际输出 `self.rebuild`（复制粘贴残留）                                                                                | `sphinx/config.py:125-132`                                                                                                      |
| 6  | 内置配置以 `Config.config_values: dict[str, _Opt]` 类属性集中声明                                                                                        | `sphinx/config.py:215-297`                                                                                                      |
| 7  | `Config.__init__` 把带点号的 override 展开为嵌套字典键（`a.b=v` → `raw['a']['b']`）                                                                         | `sphinx/config.py:309-312`                                                                                                      |
| 8  | `conf.py` 中的 `setup` 键被单独抽取为扩展钩子；`extensions` 允许逗号分隔字符串                                                                                      | `sphinx/config.py:314-322`                                                                                                      |
| 9  | `Config.read()` 在 confdir 缺少 `conf.py` 时抛 `ConfigError`                                                                                      | `sphinx/config.py:339-352`                                                                                                      |
| 10 | `convert_overrides` 按 `valid_types` 或默认值类型做字符串转换：bool 取 `'0'/'1'`、list 逗号切分、dict 禁止整体覆盖、int 解析                                               | `sphinx/config.py:354-400`                                                                                                      |
| 11 | 未注册的 override 名只产生 warning，不中断构建                                                                                                             | `sphinx/config.py:417-422`                                                                                                      |
| 12 | `__setattr__` 维护两组别名双向同步：`master_doc` 与 `root_doc`、`copyright` 与 `project_copyright`                                                         | `sphinx/config.py:434-444`                                                                                                      |
| 13 | `__getattr__` 的解析优先级为 override → conf.py 原始值 → 默认值（默认值可为 `callable(config)`），首次访问写入 `__dict__` 缓存                                            | `sphinx/config.py:446-476`                                                                                                      |
| 14 | `Config.add()` 对重复名抛 `ExtensionError`，并把 bool 型 rebuild 归一化为 `'env'` 或 `''`                                                                  | `sphinx/config.py:494-511`                                                                                                      |
| 15 | `Config.filter(rebuild)` 接受单类别字符串或类别集合，产出 `ConfigValue` 流                                                                                    | `sphinx/config.py:513-516`                                                                                                      |
| 16 | pickle 时剔除不可序列化值（置 `None`），且仅当该键 `rebuild` 非空才告警；`_options` 以 `(value, rebuild)` 落盘                                                          | `sphinx/config.py:518-553`                                                                                                      |
| 17 | `eval_config_file` 先把工作目录切到 `conf.py` 所在目录再 `exec`，命名空间预置 `__file__` 与 `tags`，并分类捕获 SyntaxError/SystemExit/ConfigError/其他异常                  | `sphinx/config.py:585-613`                                                                                                      |
| 18 | `check_confval_types` 仅发 warning（`once=True`），并做 `list→tuple`、`list/tuple/set→frozenset` 强制转换；共享非 `object` 基类即放行                             | `sphinx/config.py:777-851`                                                                                                      |
| 19 | `config-inited` 监听按优先级排序：790 弃用检查、795 版权占位符、800 源后缀/highlight/numfig/版权年份/类型检查/主域检查                                                          | `sphinx/config.py:899-914`                                                                                                      |
| 20 | 应用初始化顺序：读 conf.py → 初始化 i18n → 加载内置扩展 → 加载用户扩展 → 预加载 builder → 调用 conf.py 的 `setup` → 发 `config-inited` → 建 Project/Env/Builder              | `sphinx/application.py:263-340`                                                                                                 |
| 21 | `add_config_value(name, default, rebuild, types=(), description='')` 是扩展注册配置的唯一入口，文档明确 rebuild 三档语义                                          | `sphinx/application.py:886-940`                                                                                                 |
| 22 | 扩展元数据经 `setup(app)` 返回值收集；`parallel_read_safe` 默认 `None`、`parallel_write_safe` 默认 `True`；非 dict 返回值降级为 `{}` 并告警                              | `sphinx/extension.py:23-38`、`sphinx/registry.py:557-594`                                                                        |
| 23 | 环境缓存只以 `filter({'env'})` 判定 `CONFIG_CHANGED`；扩展集合变化单独判为 `CONFIG_EXTENSIONS_CHANGED`；HTML 侧以 `BuildInfo` 对 `filter({'html'})` 做 `stable_hash` | `sphinx/environment/__init__.py:366-371`、`sphinx/builders/html/_build_info.py:47-58`、`sphinx/builders/html/__init__.py:188-189` |
| 24 | `-D` 覆盖保持字符串并延迟转换；`-A` 落到 `html_context.<key>` 且显式尝试 `int`；`-C` 走 `confdir=None` 分支，即 `Config({}, overrides)`                                | `sphinx/cmd/build.py:364-392`、`sphinx/cmd/build.py:305-310`、`sphinx/application.py:266-273`                                     |

补充事实（不计入门槛）：

- `Project` 只接收 `source_suffix` 的键集合，`path2doc` 按后缀顺序匹配；`EXCLUDE_PATHS` 内置 `_sources`、`.#*`、`*.lproj/**`（`sphinx/project.py:20-34`、`sphinx/project.py:94-112`）。
- `get_builder_config('<builder>_<option>')` 提供 builder 变体回退（`sphinx/builders/__init__.py:860-872`）。
- `needs_extensions` 版本校验挂在 `config-inited` 优先级 800（`sphinx/extension.py:41-94`）。

## I｜洞察门（G2：5 条四元组）

### I-1 配置读取是「惰性三源合并 + 首次访问固化」

- **现象**：`config.x` 直到首次访问才计算，结果写入 `__dict__`；此后改 `_raw_config` 不影响该属性。
- **根因**：`__getattr__` 同时承担解析与缓存（`sphinx/config.py:446-476`），而 `config-inited` 各处理器通过 `setattr` 覆盖已完成求值的键。
- **影响**：在 `setup()` 阶段提前读取配置并另存副本的代码，会绕过后续规范化（如 `source_suffix`、`numfig_format`、版权年份替换），与最终配置不一致。
- **建议**：预设层把「取值」与「改写」分立——`build_config` 只产出原始值，派生计算统一放到挂 `config-inited` 的回调；禁止在 `setup` 中缓存 `app.config.*`。

### I-2 失效语义被拆到两个互不相通的层面

- **现象**：`'env'` 类变化触发环境缓存失效；`'html'` 类变化只改变 `.buildinfo` 哈希从而全量重写 HTML；`''` 类变化不触发任何重建。
- **根因**：环境层只遍历 `filter({'env'})`，HTML 层只哈希 `filter({'html'})`（`sphinx/environment/__init__.py:366-371`、`sphinx/builders/html/_build_info.py:47-58`）。
- **影响**：预设若只以 `conf.py` 变量形式暴露配置而不注册 `_Opt`，就没有失效语义——改值既不清环境也不重写页面，读者看到旧产物。
- **建议**：扩展化时逐键标注 rebuild 档位；纯 conf.py 注入场景则在文档中声明「改这些键需 `--fresh-env` 或清理构建目录」。

### I-3 类型校验是「警告 + 有限强制」，运行时无硬约束

- **现象**：类型不符只 warning 一次；`list→tuple`、`list/tuple/set→frozenset` 自动转换；共享非平凡基类即视为兼容。
- **根因**：`check_confval_types` 定位为兼容性守门而非契约执行（`sphinx/config.py:777-851`）。
- **影响**：mystx 的 `SiteConfig` 是 `TypedDict`，运行时零校验；与 Sphinx 的宽松策略叠加后，错误取值会一路带到构建期才以怪异形式暴露。
- **建议**：在 `apply_config` 现有「键集断言」之外补「取值类型断言」，复用 `frozenset`/`ENUM` 的表达能力，写入前抛 `TypeError`。

### I-4 conf.py 是脚本而非声明文件，命名空间与工作目录都被改写

- **现象**：`exec` 前工作目录切到 confdir，命名空间预置 `__file__`/`tags`；顶层 `setup` 会被当作扩展调用；`sys.exit()` 与语法错误分别转为 `ConfigError`。
- **根因**：`eval_config_file` 的 `chdir` 加命名空间注入（`sphinx/config.py:585-613`），以及 `Config.__init__` 对 `setup` 键的抽取（`sphinx/config.py:314`）。
- **影响**：预设产出的 values 若含 `setup` 键会与钩子通道冲突；预设中的相对路径隐含「相对 confdir」而非「相对仓库根」。
- **建议**：固化契约——预设禁止产出 `setup` 键，路径一律由调用方传入绝对路径或根相对路径。

### I-5 扩展加载顺序决定「配置是否可读」，注册即声明期

- **现象**：内置扩展 → 用户扩展 → 预加载 builder → conf.py 的 `setup` → `config-inited`；`Config.add` 对重名直接抛 `ExtensionError`。
- **根因**：配置寄存器随扩展加载单调增长，`add_config_value` 是唯一写入点（`sphinx/application.py:292-340`、`sphinx/config.py:494-503`）。
- **影响**：扩展在自身 `setup` 中读取他人配置，仅当对方先加载时成立；`needs_extensions` 只能做版本断言，不能保证声明顺序。
- **建议**：预设若升级为扩展，须在单个 `setup` 内一次性声明全部键，并用 `app.setup_extension` 显式表达依赖顺序；不要在 `setup` 中读取尚未声明的键。

## E｜萃取门（G3）

### 可复用模式

| 模式      | 触发场景                 | 步骤                                                                                          | 跨场景迁移                       |
| ------- | -------------------- | ------------------------------------------------------------------------------------------- | --------------------------- |
| 配置四元组声明 | 需要新增可被 CLI/CI 覆盖的配置项 | ①定名并加扩展名前缀 ②给默认值（可为 `lambda config`）③标 rebuild 档 ④给 types/ENUM 与描述 ⑤经 `add_config_value` 注册 | 任何声明式配置系统：默认值、类型、失效级别、文档四件套 |
| 三源惰性合并  | 同一键有 CLI、文件、默认三种来源   | ①override 优先 ②文件次之 ③默认兜底 ④首次访问固化 ⑤未知名告警                                                     | 应用配置中心、CI 参数注入              |
| 分类失效指纹  | 需要增量构建               | ①每个键归入失效类别 ②按类别 `filter` ③对子集做稳定哈希 ④哈希不符即全量重建                                               | 任何构建缓存或产物缓存                 |
| 别名双向同步  | 同一语义存在历史名与新名         | ①`__setattr__` 识别旧名/新名 ②同步写另一侧 ③默认值引用新名                                                     | 兼容期 API 迁移                  |
| 装配与钩子分离 | 需一次注入大量配置又保留扩展钩子     | ①纯函数产出 values ②`setup` 钩子单独返回 ③调用方分两路装配 ④写入前做键集断言                                           | 任何预设或模板型配置层                 |

### 反模式

1. **在 `setup()` 中读取未注册键**：`_options` 尚无该键，触发 `AttributeError: No such config value`。应先声明后消费。
2. **用 bool 作 rebuild**：`True/False` 被归一化为 `'env'`/`''`，无法表达 `'html'`，使「只影响输出」的键被误判为「需重读全部文档」（`sphinx/config.py:505-507`）。
3. **在 `setup` 阶段提前求值并自存副本**：错过 `config-inited` 的规范化与扩展覆写（见 I-1）。
4. **向配置注入 callable/类/模块对象**：pickle 环境时被置 `None`，且仅在 rebuild 非空时告警，形成静默的增量构建漂移（`sphinx/config.py:518-553`）。
5. **用 `-D dict=value` 整体覆盖字典**：`convert_overrides` 直接抛 `ValueError`，必须用 `-D dict.key=value` 点号形式（`sphinx/config.py:375-382`）。

### 可复用接口清单（面向 mystx presets）

| 优先级 | Sphinx 接口                                                          | 语义要点                                                        | mystx 落点                                                                                       |
| --- | ------------------------------------------------------------------ | ----------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| P0  | `app.add_config_value(name, default, rebuild, types, description)` | 声明即契约：默认值/失效档/类型/描述四元组                                      | 现有 `SiteConfig` 为手写 `TypedDict` 加手写 values，缺失效档与类型；建议引入 `SITE_CONFIG_SPEC` 单源，由 spec 生成 values |
| P0  | `check_confval_types` 的宽松策略（反向使用）                                  | 类型不符仅 warning                                               | 在 `apply_config` 键集断言之外补取值类型断言，把 warning 级问题前移为写入前异常                                           |
| P1  | `_ConfigRebuild` 类别加 `Config.filter`                               | `env/html/''` 三档决定增量边界                                      | 为每个预设键标注档位；未注册键在文档中声明需 fresh-env                                                               |
| P1  | `Config.__getattr__` 三源优先级                                         | override > conf.py > default                                | 预设可提供 `resolve(namespace, overrides)`，保证 CI 的 `-D` 覆盖仍优先于预设注入值                                 |
| P1  | `Config.__setattr__` 别名同步                                          | `copyright` 与 `project_copyright`、`master_doc` 与 `root_doc` | 预设不必同时写两个名字，文档注明由 Sphinx 同步                                                                    |
| P2  | `BuildInfo(stable_hash(config.filter(...)))`                       | 配置指纹可作缓存键                                                   | 预设可加 `config_fingerprint()`，供 CI 缓存与可复现构建比对                                                    |
| P2  | `Builder.get_builder_config('<name>_<option>')`                    | builder 变体回退查找                                              | 多 builder 变体（html/dirhtml）复用该约定，不另造前缀                                                          |
| P2  | `is_serializable` 加 `__getstate__` 守卫                              | 不可序列化值不进入环境缓存                                               | 预设侧加「禁止注入 callable/type/module」自检，前置拦截反模式 4                                                    |

## 落地优先级

1. **P0-a**：`SITE_CONFIG_SPEC` 单源化（默认值、类型、失效档、描述），`build_config` 由 spec 生成取值，`SiteConfig` 与 spec 保持一致并有测试兜底。**已落地**：`src/mystx/presets/mystx_site.py` 的 `SITE_CONFIG_SPEC` 与导入期执行一次的 `_check_spec_contract()`。
2. **P0-b**：`apply_config` 增加取值类型断言（键集契约已在导入期校验）。
3. **P1**：预设键标注 rebuild 档位；conf.py 相关文档补充「哪些键改动需 `--fresh-env`」。
4. **P2**：`config_fingerprint()` 与序列化卫生检查。

## 质量门记录

| 门      | 标准                              | 本轮结果               |
| ------ | ------------------------------- | ------------------ |
| G1 事实门 | 不少于 20 条客观事实，可验证、可追溯            | 24 条，均附文件行号        |
| G2 洞察门 | 不少于 3 条四元组洞察                    | 5 条，均含现象/根因/影响/建议  |
| G3 模式门 | 触发场景清晰、3-7 步骤、不少于 3 条反模式、可跨场景迁移 | 5 个模式、5 条反模式、8 项接口 |
| V 对抗门  | 4 视角、不少于 5 条意见                  | 按需未执行              |
| C 原子提交 | 单一职责、可独立验证                      | 按需，本页为唯一交付物        |

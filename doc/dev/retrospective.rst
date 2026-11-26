里程碑复盘：书籍化主题重构（38 提交）
======================================

.. contents:: 本页内容
   :local:
   :depth: 2

元信息
------

.. list-table::
   :width: 100%

   * - 会话
     - sc-20261126-mystx-milestone
   * - 方法
     - 七概念方法论编排，场景 1 里程碑复盘，链路 R → I → E → C
   * - 范围
     - ``origin/main..HEAD`` 的 38 个未推送提交
   * - 实测环境
     - CPython 3.14.3、Sphinx 9.2.0、pydata-sphinx-theme 0.16.1、
       myst-parser 5.2.0、ruff 0.15.10（2026-11-26 实测）
   * - 质量门
     - G1 事实门、G2 洞察门、G3 模式门、G4 原子提交门

R｜事实清单（G1：纯客观、可溯源、无因果词）
-------------------------------------------

区间与规模
~~~~~~~~~~

- F-001：``git status`` 显示分支 ``main`` 相对 ``origin/main`` 为
  ``ahead 38``，工作区无已跟踪文件改动。
- F-002：38 个提交作者均为 ``xinzo``，提交日期全部为 2026-11-24。
- F-003：``git diff --shortstat origin/main..HEAD`` 输出
  ``118 files changed, 3926 insertions(+), 571 deletions(-)``。
- F-004：Conventional Commit 类型分布为 docs 19、feat 6、fix 4、
  test 4、chore 2、refactor 2、build 1。
- F-005：区间首个提交 ``c06c284`` 内容为将 ``doc/``、``src/``、
  ``pyproject.toml`` 整体迁入 ``tests/chaos/``。

包结构与规模
~~~~~~~~~~~~

- F-006：``tests/chaos/`` 现存 570 个文件，含独立
  ``pyproject.toml`` 与完整旧包 ``tests/chaos/src/mystx``
  （config、ext、presets、tasks、themes 等模块）。
- F-007：现行发行包 ``src/mystx`` 含 ``__init__.py``、
  ``_version.py``、``book/`` 五个 Python 模块（buttons、footer、
  nav、options、sidenotes）与 ``theme/mystx/``（4 个 HTML 模板、
  3 个 CSS、1 个 JS、``theme.toml``）。
- F-008：现行自有代码实测行数为 Python 665 行、HTML 模板 52 行、
  CSS 329 行、JS 19 行；验收标准为 Python < 900 行、模板 < 60 行。
- F-009：``pyproject.toml`` 声明直接依赖两项：
  ``sphinx>=8.2,<10`` 与 ``pydata-sphinx-theme>=0.24,<0.25``；
  ``requires-python = ">=3.11"``。
- F-010：构建后端为 ``scikit-build-core>=0.11`` +
  ``setuptools-scm>=8``，``wheel.cmake`` 与 ``sdist.cmake``
  均为 ``false``。

测试与本地实测（2026-11-26）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- F-011：裸 ``pytest`` 收集 46 个用例（``tests/`` 根下 7 个
  ``test_*.py`` 加 ``conftest.py``），实测结果 45 passed、
  1 failed，失败用例为
  ``tests/test_build.py::test_current_page_is_marked``。
- F-012：该失败用例断言产出 HTML 含 ``aria-current``；本机
  pydata-sphinx-theme 版本为 0.16.1，``pyproject.toml`` 钉版区间
  为 ``>=0.24,<0.25``；``doc/dev/design/records.rst`` 记录
  PoC 在 pst 0.24.0 环境下该项验证通过。
- F-013：显式执行 ``pytest tests/unit`` 产生 15 个 collection
  error、退出码 2，错误信息均为 ``src/mystx`` 下缺失模块的
  ``FileNotFoundError``；``tests/unit/`` 现存 19 个旧测试文件。
- F-014：``pyproject.toml`` 的 ``norecursedirs`` 排除
  ``tests/chaos`` 与 ``tests/unit``，裸 ``pytest`` 不收集两者。
- F-015：``.github/workflows/tests.yml`` 的执行命令为
  ``pytest tests/unit --cov=mystx --cov-fail-under=85``，
  注释中的 117 passed、86% 覆盖率对应旧包结构。
- F-016：仓库根 ``tasks.py`` 含
  ``from mystx.tasks import doc_ns``；现行包无 ``mystx.tasks``
  模块，实测 ``python -c "import tasks"`` 与
  ``python -m invoke doc.build`` 均报
  ``src/mystx/tasks/__init__.py`` 不存在。
- F-017：``pages.yml`` 构建步骤为 ``invoke doc.build``；
  ``pyproject.toml`` 的 ``dev`` extras（pytest、build、ruff、
  myst-parser）清单中不含 ``invoke``。
- F-018：``ruff check .`` 实测输出 ``All checks passed!``；
  ``lint.yml`` 钉版 ``ruff==0.16.3``。
- F-019：``python -m sphinx -b html -W --keep-going doc``
  实测构建成功，无 warning，产物在 ``doc/_build/``。
- F-020：仓库现有 13 个 tag（``v0.1.1`` 至 ``v0.3.8``），无
  ``v0.0.1``；``_version.py`` 当前推导值为
  ``0.3.9.dev130+g7c0a7325c.d20261124``，该文件被 gitignore 不入库。

文档与外围
~~~~~~~~~~

- F-021：``doc/dev/design/`` 含 9 页设计文档（index、axioms、
  assumptions、solution、delivery、records、corrections、
  patterns、risks），其中 P0–P4 五个阶段状态均登记为已完成。
- F-022：``doc/index.rst`` 的 note 仍写「当前版本处于 P2 阶段……
  边注尚未实现」；提交 ``010117e`` 已新增脚注边注与
  ``{margin}`` 指令，提交 ``f54db57`` 已补边注开关键盘可达性。
- F-023：``CHANGELOG.md`` 的 ``[Unreleased]`` 条目描述
  presets、config、tasks、gallery 等旧包模块；
  ``git log origin/main..HEAD -- CHANGELOG.md`` 输出为空，
  38 个提交区间内该文件无变更。
- F-024：6 个 ``feat(theme)`` 提交中 4 个有同主题
  ``test(theme)`` 配对提交（全书导航、页眉按钮、边注、页脚）。
- F-025：``design/patterns.rst`` 已登记两个设计级模式：
  P-01 基座与体验层分离、P-02 能力移植四件套。
- F-026：``records.rst`` 记录 sdist 排除 ``tests/chaos`` 后
  文件数由 144 降到 76；``pyproject.toml`` 的
  ``sdist.exclude`` 含 ``tests/chaos/**``。
- F-027：``.pre-commit-config.yaml`` 含 push 阶段的本地
  ``pytest`` 钩子（裸 ``pytest``，``pass_filenames: false``）。
- F-028：``theme.toml`` 集中 6 个 ``book_*`` 选项默认值
  （``book_nav_scope``、``book_nav_depth``、
  ``book_content_width``、``book_header_buttons``、
  ``book_use_sidenotes``、``book_footer_items``）。
- F-029：``corrections.rst`` 4.14 节登记两项决定：暂不打
  ``v0.0.1`` tag；gitignore 规则改为
  ``**/src/mystx/_version.py``。
- F-030：``risks.rst`` 登记 5 项风险与缓解（双重导航、边注错位、
  PST minor 升级、借鉴代码许可、范围蔓延），仓库根存在
  ``NOTICE`` 文件。

G1 自检：事实 30 条（≥20），逐条标注来源（git 机械输出或本地
实测命令），R 节不出现因果推断词；关键版本号、命令、计数均为
实测原值。

I｜洞察（G2：四元组 = 陈述 + 证据 + 反常识 + 行动）
---------------------------------------------------

I-1 包内边界已重建，工程外围仍指向旧包
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **陈述**：38 个提交完成了发行包本体的替换，但 CI 工作流、
  任务入口、变更日志三类外围资产仍引用旧包结构，本地验证面与
  远端验证面是两套集合。
- **证据**：F-013、F-015（tests.yml 显式收集已搬走的
  ``tests/unit``）；F-016、F-017（``tasks.py`` 引用不存在的
  ``mystx.tasks``，且 dev extras 不含 invoke）；F-023
  （CHANGELOG 无新包叙事）；对照 F-011、F-019（本地裸 pytest
  与文档 ``-W`` 构建通过）。
- **反常识**：每个原子提交都附带可复现验收证据，推送后首个
  红灯却来自 38 个提交都没有修改过的工作流文件——提交级质量
  门不能替代仓库级一致性检查。
- **行动**：把工作流与任务入口纳入「移动目录」提交的检查清单，
  移动后立即全仓 grep 旧路径；本里程碑的具体修复项见文末
  行动项 A1–A3。

I-2 「入 tests 目录存档」让静态资产变成可执行测试面
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **陈述**：旧包整体迁入 ``tests/chaos`` 并保留
  ``tests/unit`` 后，仓库同时存在三份 ``mystx`` 代码实体
  （现行 ``src/mystx``、沙箱 ``tests/chaos/src/mystx``、
  环境中已安装的 editable 副本），pytest 的路径解析成为隐性契约。
- **证据**：F-005、F-006、F-007（三份实体的结构事实）；
  F-013 与 F-014 的对照（``norecursedirs`` 排除了
  ``tests/unit``，但显式路径参数仍收集并报 15 个错误）。
- **反常识**：直觉上「放进 tests 目录只是存档」，实际 pytest
  对显式传入的路径不套用递归排除规则，存档目录在 CI 命令里
  等价于现行测试源。
- **行动**：在 ``pyproject.toml`` 注释与测试文档中写明：
  ``tests/unit`` 与 ``tests/chaos`` 为旧包存档、非现行测试面；
  CI 与 pre-commit 统一只认 ``tests/`` 根的 7 个测试文件；
  中期评估删除 ``tests/unit`` 或整体并入 ``tests/chaos`` （A2、A4）。

I-3 环境与版本契约依赖人工记忆，缺乏机器前置守卫
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **陈述**：依赖钉版与 tag 策略都写在文档里，但没有任何加载期
  校验把环境错配拦截在测试运行之前；版本号推导与发版 tag 决策
  处于登记但未执行状态。
- **证据**：F-009 与 F-012 的版本错配（钉 0.24–0.25、实装
  0.16.1，唯一失败用例与该错配同现）；F-020 与 F-029
  （13 个旧 tag 使版本推导为 ``0.3.9.dev*``，``v0.0.1``
  暂缓决定已登记）。
- **反常识**：依赖区间钉得越严，环境越界时信号越间接——
  安装期没有约束冲突，现象是运行期一个 ``aria-current``
  断言失败，症状与根因之间隔了主题模板一层。
- **行动**：在 ``conftest.py`` 增加加载期版本契约断言
  （以 ``importlib.metadata`` 校验 pst 落在钉版区间，越界即
  显式 skip 并打印实际版本）；发版时按
  ``corrections.rst`` 4.14 节执行 ``git tag v0.0.1`` （A5、A6）。

G2 自检：洞察 3 条，每条含陈述、证据（引用 F 编号）、反常识、
行动四元组；三条分别覆盖外围一致性、测试面契约、环境版本守卫，
维度互不重叠。

E｜可复用模式（G3）
-------------------

模式 P-101：沙箱重写法
~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :width: 100%

   * - 成熟度
     - L1（单案例待验证），本案例为 mystx 主题化重构
   * - 适用场景
     - 同仓库内对包做职责收缩或整体重写，同时需要保留旧实现
       作为回归参考与资产存档
   * - 不适用
     - 小版本迭代与单点 bug 修复；需要双版本长期并行维护的场景
       （应开独立分支或独立包名）

核心步骤（6 步）
++++++++++++++++

1. **整体移动先行**：旧树一次性移入沙箱目录（如
   ``tests/chaos``）并单独成提，不与新代码混提。
2. **空骨架增量重建**：新包从最小骨架起步，按阶段（本案例
   P0–P4）交付，每个特性保持 ``feat → test → docs`` 三连提。
3. **打包清单显式收口**：``sdist.include/exclude`` 与
   ``wheel.packages`` 明确排除沙箱，解包后核对文件数。
4. **测试发现面同步**：``testpaths``、``norecursedirs`` 与
   CI 调用路径一起改，禁止只改其中一处。
5. **外围引用全仓对账**：工作流、任务入口、pre-commit、
   CHANGELOG、README 逐个 grep 旧模块名，命中点逐个裁决。
6. **版本策略登记**：旧 tag 共存规则与新起点 tag 写入设计
   文档的待确认项，发版动作与代码改动解耦。

反模式（均来自本案例实测教训）
++++++++++++++++++++++++++++++

1. **只挪代码不改 CI**：显式路径绕过 ``norecursedirs``，
   存档测试被当作现行测试执行（本案例 15 个 collection error，
   见 F-013/F-015）。
2. **留适配层不验导入**：薄适配文件引用已搬走的模块，日常
   不 import 就不可见（本案例 ``tasks.py`` 断链，见 F-016）。
3. **变更日志沿用旧叙事**：CHANGELOG 仍描述旧包模块，读者
   无法从日志识别包形态已经替换（见 F-023）。

检验标准
++++++++

- 裸 ``pytest`` 与 CI 显式测试命令在干净环境结果一致；
- 全仓 grep 旧模块名，命中点仅出现在沙箱目录与设计文档；
- wheel/sdist 解包后无沙箱文件，资源文件数与打包清单对账一致；
- 文档 ``-W`` 构建零 warning。

跨场景迁移
++++++++++

前端工程把旧 Webpack 应用移入 ``legacy/`` 并用 Vite 重写时，
同一模式适用于 CI 流水线、e2e 测试发现路径与部署入口的同步
收口；数据团队归档旧 ETL 脚本时，调度器 DAG 中的任务引用
清理对应第 5 步的外围对账。

G3 自检：模式名 5 字；含适用/不适用边界、6 个可执行步骤、
3 个来自实测的反模式、4 条检验标准与 2 个跨领域迁移示例；
单案例标注 L1，不冒充已验证模式。设计级模式 P-01/P-02 仍以
``design/patterns.rst`` 为权威来源，本页不重复登记。

建议行动项（不在本次提交范围，供后续排期）
------------------------------------------

.. list-table::
   :header-rows: 1
   :width: 100%

   * - 编号
     - 行动项
     - 验收标准
     - 优先级
   * - A1
     - tests.yml 切换到现行测试面，重设覆盖率口径
     - CI 收集 46 个用例并通过；覆盖率门禁按 ``src/mystx``
       重新标定
     - 高
   * - A2
     - 修复 pages.yml 构建链路
     - 二选一：改 ``sphinx`` 直构，或补 invoke 依赖并重写
       tasks 入口
     - 高
   * - A3
     - CHANGELOG 增主题化重构版本段
     - 新段描述现行包形态，旧包条目标注归属 ``tests/chaos``
     - 中
   * - A4
     - 更新 doc/index.rst 的 P2 注记
     - P2 注记改为 P4 现状，边注描述与 F-022 实际能力一致
     - 中
   * - A5
     - conftest 增加 pst 版本契约守卫
     - 越界环境显式 skip 并打印实际版本，契约内环境行为不变
     - 中
   * - A6
     - 发版时打 ``v0.0.1`` tag
     - setuptools-scm 推导值为 0.0.1，与设计文档版本起点一致
     - 低

实测证据台账
------------

.. list-table::
   :header-rows: 1
   :width: 100%

   * - 命令
     - 实测结果（2026-11-26）
   * - ``pytest -q``
     - 45 passed, 1 failed（F-011/F-012）
   * - ``pytest tests/unit -q``
     - 15 collection errors，退出码 2（F-013）
   * - ``ruff check .``
     - All checks passed（F-018）
   * - ``sphinx -b html -W doc``
     - 构建成功，零 warning（F-019）
   * - ``python -c "import tasks"``
     - FileNotFoundError，退出码 1（F-016）
   * - ``git status --short``
     - 无输出，工作区干净（F-001）

边界与未覆盖项
--------------

- 本复盘只覆盖 ``origin/main..HEAD`` 的 38 个提交，不含
  ``origin/main`` 之前的历史。
- 浏览器矩阵、视觉回归与 axe 可访问性扫描未在本次复盘中执行；
  设计文档记录的视口矩阵与键盘可达性结论以
  ``design/corrections.rst`` 4.17 节为准。
- ``python -m build`` 的 wheel/sdist 全量打包验证未重跑，
  打包结论引用 ``design/records.rst`` 的既有验收记录。
- 本机 pst 版本（0.16.1）不在项目钉版区间内，F-011 的 1 个
  失败用例尚需在钉版区间环境（pst 0.24.x）复测后才能定性为
  环境问题或代码缺陷，本页只记录实测现象，不作因果定性。

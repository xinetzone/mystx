# GitHub Readme Stats

本文档介绍在 Sphinx 文档中使用 GitHub Readme Stats 的指令（模块：{mod}`~mystx.ext.github_readme_stats`），通过三条指令嵌入 GitHub Readme Stats 卡片：用户统计、常用语言、置顶仓库。

- 外部服务：`https://github-readme-stats.vercel.app/`
- 参考 [GitHub Readme Stats 项目文档](https://github.com/anuraghazra/github-readme-stats)

## 快速开始

在你的扩展入口或 `conf.py` 中注册指令：

```python
extension = ["mystx.ext.github_readme_stats"]
```

## 用法示例

::::{myst-example}
:::{github-stats}
:username: xinetzone
:theme: dark
:show_icons:
:hide: issues,contribs
:::
::::

::::{myst-example}
```{github-top-langs}
:username: xinetzone
:layout: compact
:theme: dark
:langs_count: 8
```
::::

::::{myst-example}
```{github-pinned-repo}
:username: xinetzone
:repo: mystx
:theme: dark
```
::::

::::{myst-example}
```{github-pinned-repo}
:link: https://xinetzone.github.io/tao
:username: xinetzone
:repo: tao
:theme: dark
```
::::


## 指令与选项说明

### github-stats（用户统计卡片）
- `username`（必填）：GitHub 用户名。
- `theme`（可选）：主题名称，默认 `default`。
- `show_icons`（可选 flag）：出现该选项即显示图标。
- `hide`（可选）：以逗号分隔的统计项列表，例如 `issues,contribs`。

上游可选项（需扩展）：
- `commits_year`：指定年份统计提交数（格式 `YYYY`）。
- `show`：展示额外统计项（逗号分隔）：`reviews`、`discussions_started`、`discussions_answered`、`prs_merged`、`prs_merged_percentage`。
- `include_all_commits`：包含所有历史提交。
- `count_private`：包含私有贡献统计。
- `hide_rank`：隐藏等级环形标识。
- `rank_icon`：等级图标样式（如 `percentile`）。
- `custom_title`：自定义卡片标题。
- `hide_border`：隐藏卡片边框。
- `card_width`：卡片宽度（像素）。
- `locale`：界面语言（如 `zh-CN`）。
- 颜色与背景：`text_color`、`title_color`、`icon_color`、`border_color`、`ring_color`、`bg_color`（支持渐变：`DEG,hex1,hex2`）。
- `disable_animations`：禁用卡片动画。

### github-top-langs（常用语言卡片）
- `username`（必填）：GitHub 用户名。
- `layout`（可选）：布局样式，默认 `compact`。
- `theme`（可选）：主题名称，默认 `default`。
- `langs_count`（可选）：展示语言数量，默认 `6`。

上游可选项（需扩展）：
- `hide`：隐藏指定语言（逗号分隔）。
- `exclude_repo`：排除指定仓库（逗号分隔）。
- `card_width`：卡片宽度（像素）。
- `hide_progress`：隐藏进度条。
- 统计格式：切换显示格式（如百分比/字节大小）。
- 扩展布局：`donut`、`donut-vertical`、`pie` 等。

### github-pinned-repo（置顶仓库卡片）
- `username`（必填）：GitHub 用户名。
- `repo`（必填）：仓库名。
- `theme`（可选）：主题名称，默认 `default`。
- `link`（可选）：点击卡片跳转的链接地址。

上游可选项（需扩展）：
- `show_owner`：显示仓库所有者。
- `custom_title`：自定义标题。
- `hide_border`：隐藏边框。
- `disable_animations`：禁用动画。
- 颜色与背景：`title_color`、`text_color`、`icon_color`、`border_color`、`bg_color`。

## 注意事项
- 这些指令依赖外部服务 `https://github-readme-stats.vercel.app/`，渲染结果与可选参数由该服务决定。
- 仅支持上述列出的选项；若需更多定制（如 `commits_year`、`show` 等），请参考上游项目并扩展指令的 `option_spec`。
- 主题示例（由上游项目内置）：`dark`、`radical`、`merko`、`gruvbox`、`tokyonight`、`onedark`、`cobalt`、`synthwave`、`highcontrast`、`dracula` 等。
- 如需显示私有统计或提升速率限制，请考虑按照上游说明在自己的平台部署该服务并配置令牌。

## 相关链接

- 参考项目主页：[GitHub Readme Stats](https://github.com/anuraghazra/github-readme-stats)
- Stats 卡片文档：详见项目页面的 “GitHub Stats Card” 章节
- Top Languages 卡片文档：详见项目页面的 “Top Languages Card” 章节
- Extra Pins（置顶仓库）文档：详见项目页面的 “GitHub Extra Pins” 章节

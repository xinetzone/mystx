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
:username: xinetzone
:repo: tao
:theme: dark
:link: https://xinetzone.github.io/tao
```
::::

::::{myst-example}
:::{github-wakatime}
:username: xinetzone
:layout: compact
:theme: tokyonight
:range: all_time
:::
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

### github-wakatime（WakaTime 统计卡片）
- `username`（必填）：WakaTime 用户名。
- `theme`（可选）：主题名称，默认 `default`。
- `layout`（可选）：布局样式，示例 `compact`。
- `range`（可选）：统计范围（如 `last_7_days`、`last_30_days`、`last_6_months`、`last_year`、`all_time`）。
- `api_domain`（可选）：自定义 API 域名（如 Hakatime/Wakapi）。
- `custom_title`（可选）：自定义标题。
- `hide_title`（可选 flag）：隐藏标题。
- `hide_border`（可选 flag）：隐藏边框。

注意：仅公开的 WakaTime 资料会显示统计数据；更多细节与演示参见[项目主页的 “WakaTime Stats Card” 章节](https://github.com/anuraghazra/github-readme-stats/tree/master#wakatime-stats-card)。
## 注意事项
- 这些指令依赖外部服务 `https://github-readme-stats.vercel.app/`，渲染结果与可选参数由该服务决定。
- 仅支持上述列出的选项；若需更多定制（如 `commits_year`、`show` 等），请参考上游项目并扩展指令的 `option_spec`。
- 可用主题（适用于 Stats/Repo/Gist/Top Languages/WakaTime）：`default`、`transparent`、`shadow_red`、`shadow_green`、`shadow_blue`、`dark`、`radical`、`merko`、`gruvbox`、`gruvbox_light`、`tokyonight`、`onedark`、`cobalt`、`synthwave`、`highcontrast`、`dracula`、`prussian`、`monokai`、`vue`、`vue-dark`、`shades-of-purple`、`nightowl`、`buefy`、`blue-green`、`algolia`、`great-gatsby`、`darcula`、`bear`、`solarized-dark`、`solarized-light`、`chartreuse-dark`、`nord`、`gotham`、`material-palenight`、`graywhite`、`vision-friendly-dark`、`ayu-mirage`、`midnight-purple`、`calm`、`flag-india`、`omni`、`react`、`jolly`、`maroongold`、`yeblu`、`blueberry`、`slateorange`、`kacho_ga`、`outrun`、`ocean_dark`、`city_lights`、`github_dark`、`github_dark_dimmed`、`discord_old_blurple`、`aura_dark`、`panda`、`noctis_minimus`、`cobalt2`、`swift`、`aura`、`apprentice`、`moltack`、`codeSTACKr`、`rose_pine`、`catppuccin_latte`、`catppuccin_mocha`、`date_night`、`one_dark_pro`、`rose`、`holi`、`neon`、`blue_navy`、`calm_pink`、`ambient_gradient`。
- Repo 卡片专属：`default_repocard`。
- 完整主题列表与预览：[Themes README](https://github.com/anuraghazra/github-readme-stats/blob/master/themes/README.md)
- 如需显示私有统计或提升速率限制，请考虑按照上游说明在自己的平台部署该服务并配置令牌。

## 更多主题示例

为便于对比，以下示例仅更换 `:theme:` 选项。

### Stats 主题示例

::::{myst-example}
:::{github-stats}
:username: xinetzone
:theme: dark
:show_icons:
:::
::::

::::{myst-example}
:::{github-stats}
:username: xinetzone
:theme: tokyonight
:show_icons:
:::
::::

::::{myst-example}
:::{github-stats}
:username: xinetzone
:theme: gruvbox
:show_icons:
:::
::::

::::{myst-example}
:::{github-stats}
:username: xinetzone
:theme: dracula
:show_icons:
:::
::::

::::{myst-example}
:::{github-stats}
:username: xinetzone
:theme: github_dark
:show_icons:
:::
::::

::::{myst-example}
:::{github-stats}
:username: xinetzone
:theme: catppuccin_mocha
:show_icons:
:::
::::

::::{myst-example}
:::{github-stats}
:username: xinetzone
:theme: nord
:show_icons:
:::
::::

::::{myst-example}
:::{github-stats}
:username: xinetzone
:theme: aura_dark
:show_icons:
:::
::::

### Top Languages 主题示例

::::{myst-example}
```{github-top-langs}
:username: xinetzone
:layout: compact
:theme: radical
:langs_count: 8
```
::::

::::{myst-example}
```{github-top-langs}
:username: xinetzone
:layout: compact
:theme: monokai
:langs_count: 8
```
::::

::::{myst-example}
```{github-top-langs}
:username: xinetzone
:layout: compact
:theme: prussian
:langs_count: 8
```
::::

::::{myst-example}
```{github-top-langs}
:username: xinetzone
:layout: compact
:theme: calm
:langs_count: 8
```
::::

### Repo 卡片主题示例

::::{myst-example}
```{github-pinned-repo}
:username: xinetzone
:repo: mystx
:theme: default_repocard
```
::::

::::{myst-example}
```{github-pinned-repo}
:username: xinetzone
:repo: tao
:theme: cobalt2
:link: https://xinetzone.github.io/tao
```
::::

::::{myst-example}
```{github-pinned-repo}
:username: xinetzone
:repo: mystx
:theme: moltack
```
::::

## 相关链接

- 参考项目主页：[GitHub Readme Stats](https://github.com/anuraghazra/github-readme-stats)
- Stats 卡片文档：详见项目页面的 “GitHub Stats Card” 章节
- Top Languages 卡片文档：详见项目页面的 “Top Languages Card” 章节
- Extra Pins（置顶仓库）文档：详见项目页面的 “GitHub Extra Pins” 章节
- WakaTime 卡片文档：详见项目页面的 “WakaTime Stats Card” 章节

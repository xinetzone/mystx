"""主题、静态资源、字体增强与站点前端配置。"""
from mystx.fonts import configure_optional_matplotlib_fonts

from .common import ROOT, has_module

# 排除文件和目录模式
# README.md 面向仓库读者（徽章 / 安装命令 / 特性列表），不参与站点构建；
# 文档站的根入口见 index.md，仓库 README 通过「相关入口」链接引用。
exclude_patterns = [
    "_build",      # 构建输出目录
    "Thumbs.db",   # 缩略图数据库
    ".DS_Store",    # macOS 系统文件
    "README.md",   # 仓库 README 不纳入文档树
]

# 静态资源目录，用于存放CSS、JavaScript、图片等
html_static_path = ["_static"]
html_css_files = ["local.css", "font.css"]
# 文档的最后更新时间格式
html_last_updated_fmt = "%Y-%m-%d, %H:%M:%S"
templates_path = ["_templates"]

# 主题选择：mystx 优先，其次书系主题，最后退到 alabaster
if has_module("mystx"):
    html_theme = "mystx"
elif has_module("sphinx_book_theme"):
    html_theme = "sphinx_book_theme"
else:
    html_theme = "alabaster"
html_title = "Sphinx mystx Theme"  # 文档标题
html_logo = "_static/images/logo.jpg"  # 文档logo
html_favicon = "_static/images/favicon.jpg"  # 文档favicon
html_copy_source = True  # 是否在文档中包含源文件链接

# 可选：matplotlib 字体配置
# 字体增强的「包不可用 / 目录缺失 / 调用失败」三重守卫由包内
# configure_optional_matplotlib_fonts 统一实现：任一不满足只记日志、不阻断。
# ・RTD 仅安装 .[doc]（见 .readthedocs.yml），其依赖清单不含 taolib；
# ・浏览器端代码字体由 _static/font.css 的 @font-face 独立提供，与本块无关。
configure_optional_matplotlib_fonts(
    ROOT / "doc/_static/fonts",
    families=("Maple Mono NF CN", "Noto Color Emoji"),
)

# ================================= thebe 交互式功能配置 =================================
# use_thebe = True  # 是否开启Thebe功能（默认关闭）
# thebe_config = {
#     "repository_url": f"https://github.com/xinetzone/{project}",
#     "repository_branch": "main",
#     "selector": "div.highlight",
#     # "selector": ".thebe",
#     # "selector_input": "",
#     # "selector_output": "",
#     # "codemirror-theme": "blackboard",  # Doesn't currently work
#     # "always_load": True,  # To load thebe on every page
# }

# ================================= 版本切换器配置 =================================
# 用**相对路径**指向本仓库的清单文件，不要写 http(s) 绝对 URL：
# pydata 对绝对 URL 会在构建期发 requests.get 校验，读不到即 warning；而本仓库
# CI 用 harden-runner 阻断出网（白名单不含 readthedocs.io），那道校验在 CI 上
# 必然失败——既产生噪声，又让这道校验永远走不到「通过」分支（守卫空转）；
# 且首次部署前该文件还不存在，绝对 URL 必然形成自举死锁。
# 相对路径改为读本地文件，校验照旧生效，前端按站点根解析，两条通道都取得到。
version_switcher_json_url = "_static/switcher.json"

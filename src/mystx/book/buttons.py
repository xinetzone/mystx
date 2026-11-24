"""页眉工具箱：把配置项翻译成按钮数据，模板只负责渲染。

按钮是数据，不是模板。URL 规则、图标与"链接还是脚本"都集中在本模块，可单测；
模板只有一个循环：有 ``javascript`` 就输出 ``<button>``，否则输出 ``<a>``。
"""

from __future__ import annotations

from typing import Any

_PROVIDERS: dict[str, dict[str, str]] = {
    "github": {
        "base": "https://github.com",
        "edit": "/edit/",
        "blob": "/blob/",
        "icon": "fa-brands fa-github",
    },
    "gitlab": {
        "base": "https://gitlab.com",
        "edit": "/-/edit/",
        "blob": "/-/blob/",
        "icon": "fa-brands fa-gitlab",
    },
    "bitbucket": {
        "base": "https://bitbucket.org",
        "edit": "/src/",
        "blob": "/src/",
        "icon": "fa-brands fa-bitbucket",
    },
}

_ICONS = {
    "download": "fa-solid fa-download",
    "fullscreen": "fa-solid fa-expand",
    "source": "fa-solid fa-file-code",
    "edit": "fa-solid fa-pen-to-square",
    "issue": "fa-solid fa-circle-exclamation",
    "repo": "",
}


def _repo_parts(context: dict[str, Any]) -> dict[str, str] | None:
    """从 ``html_context`` 读取仓库坐标；缺任一项即视为未配置。"""
    for name, meta in _PROVIDERS.items():
        user = context.get(f"{name}_user")
        repo = context.get(f"{name}_repo")
        version = context.get(f"{name}_version")
        if user and repo and version:
            base = context.get(f"{name}_url") or meta["base"]
            return {
                "provider": name,
                "base": str(base).rstrip("/"),
                "user": str(user),
                "repo": str(repo),
                "version": str(version),
                "edit": meta["edit"],
                "blob": meta["blob"],
                "icon": meta["icon"],
            }
    return None


def _relative_path(pagename: str, context: dict[str, Any]) -> str:
    doc_path = str(context.get("doc_path", "") or "").strip("/")
    file_name = f"{pagename}{context.get('page_source_suffix', '')}"
    return f"{doc_path}/{file_name}" if doc_path else file_name


def build_buttons(
    pagename: str,
    context: dict[str, Any],
    names: list[str] | tuple[str, ...],
) -> list[dict[str, str]]:
    """按配置顺序生成按钮列表；缺数据的按钮直接省略。"""
    repo = _repo_parts(context)
    rel_path = _relative_path(pagename, context)
    buttons: list[dict[str, str]] = []

    for name in names:
        if name == "download":
            if not context.get("sourcename"):
                continue
            buttons.append(
                {
                    "type": "download",
                    "label": "Download this page",
                    "icon": _ICONS["download"],
                    "href": f"_sources/{context['sourcename']}",
                    "download": True,
                    "tooltip": "Download this page",
                }
            )
        elif name == "fullscreen":
            buttons.append(
                {
                    "type": "javascript",
                    "label": "Fullscreen mode",
                    "icon": _ICONS["fullscreen"],
                    "javascript": "toggleFullscreen()",
                    "tooltip": "Fullscreen mode",
                }
            )
        elif name in {"repo", "edit", "source", "issue"} and repo:
            buttons.append(_repo_button(name, repo, rel_path, pagename))
    return buttons


def _repo_button(
    name: str,
    repo: dict[str, str],
    rel_path: str,
    pagename: str,
) -> dict[str, str]:
    base = repo["base"]
    slug = f"{repo['user']}/{repo['repo']}"
    version = repo["version"]

    if name == "repo":
        url = f"{base}/{slug}"
        label, icon = "Source repository", repo["icon"]
    elif name == "edit":
        url = f"{base}/{slug}{repo['edit']}{version}/{rel_path}"
        label, icon = "Suggest edit", _ICONS["edit"]
    elif name == "source":
        sep = "&" if "?" in rel_path else "?"
        url = f"{base}/{slug}{repo['blob']}{version}/{rel_path}{sep}plain=1"
        if repo["provider"] == "bitbucket":
            url = f"{base}/{slug}{repo['blob']}{version}/{rel_path}"
        label, icon = "View source", _ICONS["source"]
    else:  # issue
        url = f"{base}/{slug}/issues/new?title=Issue on page /{pagename}.html"
        label, icon = "Open an issue", _ICONS["issue"]

    return {
        "type": "link",
        "label": label,
        "icon": icon,
        "href": url,
        "tooltip": label,
    }

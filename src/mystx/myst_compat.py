"""MyST 兼容钩子：frontmatter 日期加引号、去除注入的重复 H1。

两个开关由环境变量控制：``MYSTX_MYST_COMPAT_*`` 为规范前缀，``SW_MYST_COMPAT_*``
是计划在 mystx 0.7 移除的过渡别名——到期时应连同 ``_read_switch`` 里的别名分支
一并删除，不必再保留空壳判断。
"""
import os
import re

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.util import logging

_logger = logging.getLogger(__name__)

_ISO_DATETIME_RE = re.compile(
    r"([A-Za-z_][A-Za-z0-9_-]*\s*:\s*)"
    r"(\d{4}-\d{2}-\d{2}(?:[Tt]\d{2}:\d{2}:\d{2}(?:[+-]\d{2}:\d{2}|Z)?)?)"
)
_FM_DELIM = re.compile(r"^(?:---|\+\+\+|\.\.\.)\s*$", re.MULTILINE)

_DEPRECATED_PREFIX_NOTICE = (
    "Deprecated: environment variable prefix SW_MYST_COMPAT_* is deprecated, "
    "use MYSTX_MYST_COMPAT_* instead (removed in mystx>=0.7)"
)

_ENV_QUOTE_DATES = True
_ENV_DEDUPE_H1 = True


def _read_switch(name: str) -> bool:
    """读取单个开关：规范前缀优先，过渡别名次之（命中记一次弃用日志），缺省启用。

    取值 ``0`` / ``false`` / ``off``（不分大小写）表示关闭，其余非空值表示开启。
    """
    for prefix in ("MYSTX_MYST_COMPAT_", "SW_MYST_COMPAT_"):
        value = os.environ.get(prefix + name)
        if value is None:
            continue
        if prefix == "SW_MYST_COMPAT_":
            _logger.info(_DEPRECATED_PREFIX_NOTICE)
        return value.lower() not in {"0", "false", "off"}
    return True


def _reload_env_settings() -> None:
    """重读两个开关，供测试 monkeypatch 或进程内刷新使用。"""
    global _ENV_QUOTE_DATES, _ENV_DEDUPE_H1
    _ENV_QUOTE_DATES = _read_switch("QUOTE_DATES")
    _ENV_DEDUPE_H1 = _read_switch("DEDUPE_H1")


_reload_env_settings()


def quote_frontmatter_dates(app: Sphinx, docname: str, source: list[str]) -> None:
    """``source-read`` 钩子：给 **YAML frontmatter** 内无引号的裸日期补双引号。

    myst_parser 会把裸日期解析为 :class:`datetime.date`，后续 ``json.dumps``
    抛 ``Object of type date is not JSON serializable``。仅处理首行 ``---`` 的
    YAML：TOML frontmatter 的日期是原生类型，加引号反而改变其类型。

    只在「日期本身构成完整值」时加引号（值尾为行尾、空白、``}``/``]``/``,``
    或行内注释），避免误伤以日期开头的长中文值。

    关闭方式：``MYSTX_MYST_COMPAT_QUOTE_DATES=0``（旧别名同样有效）。
    """
    if not _ENV_QUOTE_DATES:
        return
    text = source[0]
    delims = list(_FM_DELIM.finditer(text))
    if len(delims) < 2 or delims[0].start() != 0:
        return
    if text[: delims[0].end()].splitlines()[0].strip() != "---":
        return
    frontmatter = text[delims[0].end() : delims[1].start()]

    def _quote_if_complete(match: re.Match) -> str:
        tail = frontmatter[match.end() :].split("\n", 1)[0].strip()
        if tail == "" or tail[-1] in "}]," or tail.startswith("#"):
            return match.expand(r'\1"\2"')
        return match.group(0)

    quoted = _ISO_DATETIME_RE.sub(_quote_if_complete, frontmatter)
    if quoted != frontmatter:
        source[0] = text[: delims[0].end()] + quoted + text[delims[1].start() :]


def dedupe_injected_h1(app: Sphinx, doctree: nodes.document) -> None:
    """``doctree-read`` 钩子：去除 ``myst_title_to_header`` 注入的空壳 H1。

    正文自带 H1 时，注入项使 doctree 出现两个顶级 section；空壳 H1 会被
    ``TocTreeCollector`` 生成带 ``#anchor`` 的 TOC 条目，pydata/书系主题随即
    删除整条 ``li``（连同其子 ``ul``），侧边栏退化为只剩一级导航。

    注册优先级必须 ``<500``（TocTreeCollector 的默认值），确保在
    ``process_doc`` 构建 ``env.tocs`` 之前生效。

    关闭方式：``MYSTX_MYST_COMPAT_DEDUPE_H1=0``（旧别名同样有效）。
    """
    if not _ENV_DEDUPE_H1:
        return
    sections = [n for n in doctree.children if isinstance(n, nodes.section)]
    if len(sections) < 2:
        return
    if len(sections[0].children) <= 1:
        doctree.remove(sections[0])


def register_hooks(app: Sphinx) -> None:
    """在 Sphinx app 上统一注册本模块的两个兼容性钩子。"""
    app.connect("source-read", quote_frontmatter_dates)
    app.connect("doctree-read", dedupe_injected_h1, priority=400)

import os
import re as _re
from sphinx.util import logging; _logger = logging.getLogger(__name__)

_ISO_DATETIME_RE = _re.compile(
    r"([A-Za-z_][A-Za-z0-9_-]*\s*:\s*)"
    r"(\d{4}-\d{2}-\d{2}(?:[Tt]\d{2}:\d{2}:\d{2}(?:[+-]\d{2}:\d{2}|Z)?)?)"
)
_FM_DELIM = _re.compile(r"^(?:---|\+\+\+|\.\.\.)\s*$", _re.MULTILINE)


_ENV_QUOTE_DATES = True
_ENV_DEDUPE_H1 = True


def _reload_env_settings() -> None:
    """Reload module-level environment-variable toggles.

    Useful for pytest monkeypatch or in-process runtime refresh.

    Precedence for each toggle:
      1. ``MYSTX_MYST_COMPAT_*`` env var (new canonical prefix)
      2. ``SW_MYST_COMPAT_*`` env var (deprecated alias, logs info if hit)
      3. Default: enabled (``True``)

    Values ``"0"`` / ``"false"`` / ``"off"`` (case-insensitive) disable the toggle;
    any other non-empty value enables it.
    """
    global _ENV_QUOTE_DATES, _ENV_DEDUPE_H1

    # --- QUOTE_DATES ---
    val = os.environ.get("MYSTX_MYST_COMPAT_QUOTE_DATES")
    if val is None:
        val = os.environ.get("SW_MYST_COMPAT_QUOTE_DATES")
        if val is not None:
            _logger.info("Deprecated: environment variable prefix SW_MYST_COMPAT_* is deprecated, use MYSTX_MYST_COMPAT_* instead (removed in mystx>=0.7)")
    if val is None:
        _ENV_QUOTE_DATES = True
    else:
        _ENV_QUOTE_DATES = val.lower() not in {"0", "false", "off"}

    # --- DEDUPE_H1 ---
    val = os.environ.get("MYSTX_MYST_COMPAT_DEDUPE_H1")
    if val is None:
        val = os.environ.get("SW_MYST_COMPAT_DEDUPE_H1")
        if val is not None:
            _logger.info("Deprecated: environment variable prefix SW_MYST_COMPAT_* is deprecated, use MYSTX_MYST_COMPAT_* instead (removed in mystx>=0.7)")
    if val is None:
        _ENV_DEDUPE_H1 = True
    else:
        _ENV_DEDUPE_H1 = val.lower() not in {"0", "false", "off"}


_reload_env_settings()


def quote_frontmatter_dates(app: "Sphinx", docname: str, source: list[str]) -> None:
    """``source-read`` 钩子：为 **YAML frontmatter** 内无引号的裸日期/时间戳补双引号。

    解决的问题（对应原 awesome-okf-xs/doc/conf.py L183-L226）：
      myst_parser 会把无引号的 YAML 日期解析为 :class:`datetime.date`，
      进而在 ``dict_to_fm_field_list`` 中 ``json.dumps`` 时抛
      ``Object of type date is not JSON serializable``。

    **仅对 YAML 格式（首行 ``---`` 定界符）生效：**
    TOML frontmatter 的日期是原生 ISO8601 类型，不需要也不应加引号——
    盲目加引号会让 TOML 解析器把日期当字符串，导致类型改变。

    只在「日期/时间戳本身构成完整值」时加引号——值尾允许行尾、行内空白换行，
    或 flow map/list 的闭合标点（``}`` / ``]`` / ``,``）。避免误伤以
    日期开头的长纯标量，例如 ``description: 2026-08-28对博文……``（早期版本
    无条件替换会在中文值中间插入孤立引号，导致 ``Malformed YAML [myst.topmatter]``）。

    可通过环境变量 ``MYSTX_MYST_COMPAT_QUOTE_DATES=0`` 关闭本钩子
    (backward-compat alias SW_MYST_COMPAT_QUOTE_DATES preserved)。
    """
    if not _ENV_QUOTE_DATES:
        return
    text = source[0]
    delims = list(_FM_DELIM.finditer(text))
    if len(delims) < 2 or delims[0].start() != 0:
        return
    first_line = text[: delims[0].end()].splitlines()[0].strip()
    if first_line != "---":
        return
    fm = text[delims[0].end(): delims[1].start()]

    def _repl(match: _re.Match) -> str:
        line_tail = fm[match.end():].split("\n", 1)[0].strip()
        if line_tail == "" or line_tail[-1] in "}]," or line_tail.startswith("#"):
            return match.expand(r'\1"\2"')
        return match.group(0)

    quoted = _ISO_DATETIME_RE.sub(_repl, fm)
    if quoted != fm:
        source[0] = text[: delims[0].end()] + quoted + text[delims[1].start():]


def dedupe_injected_h1(app: "Sphinx", doctree: "nodes.document") -> None:
    """``doctree-read`` 钩子：去除 ``myst_title_to_header`` 注入的重复 H1。

    解决的问题（对应原 awesome-okf-xs/doc/conf.py L229-L250）：
      ``myst_title_to_header = True`` 会把 frontmatter ``title`` 注入为文档首个 H1；
      若正文自带 H1，doctree 会有两个顶级 section。注入项仅含标题、无正文内容，
      Sphinx ``TocTreeCollector`` 为其生成带 ``#anchor`` 链接的 TOC 条目；
      ``pydata/sphinx_book_theme`` 侧边栏整体删除含 ``#anchor`` 的 ``li``
      （连同嵌套子 ``ul`` 一起 ``decompose``），导致侧边栏只剩一级导航。

    必须以 ``priority<500`` 注册（小于 TocTreeCollector 默认的 500），
    确保在 ``process_doc`` 构建 ``env.tocs`` 之前清理 doctree。

    可通过环境变量 ``MYSTX_MYST_COMPAT_DEDUPE_H1=0`` 关闭本钩子
    (backward-compat alias SW_MYST_COMPAT_DEDUPE_H1 preserved)。
    """
    if not _ENV_DEDUPE_H1:
        return
    from docutils import nodes

    sections = [n for n in doctree.children if isinstance(n, nodes.section)]
    if len(sections) < 2:
        return
    first = sections[0]
    if len(first.children) <= 1:
        doctree.remove(first)


def register_hooks(app: "Sphinx") -> None:
    """在 Sphinx app 上统一注册本模块的两个兼容性钩子。"""
    app.connect("source-read", quote_frontmatter_dates)
    app.connect("doctree-read", dedupe_injected_h1, priority=400)

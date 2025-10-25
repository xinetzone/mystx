"""live_preview — 在浏览器中实时预览 MyST 文档

基于 Docutils 与 MyST-Parser，将输入的 MyST 文本转换为 HTML 或其它格式，
并在 PyScript/Pyodide 环境中通过 DOM 事件实现即时刷新。

- 覆盖简化的 HTML 翻译器与 Writer，仅输出 body 内容并禁用样式注入；
- 解析 YAML 配置以设置 Docutils 转换参数，收集并显示警告信息；
- 通过页面输入与选择器，实时触发转换并更新预览区域。
"""
import traceback
from io import StringIO

import yaml
from docutils.core import publish_string
from docutils.frontend import filter_settings_spec
from docutils.writers.html5_polyglot import HTMLTranslator, Writer

from dataclasses import dataclass
from myst_parser import __version__
from myst_parser.parsers.docutils_ import Parser
HTML_FORMATS = {"html", "html4", "html5", "html5_polyglot"}

def is_html_format(name: str) -> bool:
    try:
        return any(fmt in (name or "").lower() for fmt in HTML_FORMATS)
    except Exception:
        return False

PARSER = Parser()

MIN_INTERVAL_MS = 250
_last_run_ms = 0.0
_last_config = ""
_last_input = ""
_last_format = ""

class SimpleTranslator(HTMLTranslator):
    """简化的 HTML 翻译器。

    - 为代码块（literal_block）追加 ``highlight`` 类，便于外部样式统一高亮；
    - 禁用样式表插入，避免在页面中重复注入样式。
    """
    def visit_literal_block(self, node):
        """处理代码块节点，追加类名后交由父类渲染。"""
        node["classes"].append("highlight")
        return super().visit_literal_block(node)

    def stylesheet_call(self, *args, **kwargs):
        """覆盖样式表插入逻辑，返回空字符串以禁用样式输出。"""
        return ""


class SimpleWriter(Writer):
    """简化的 HTML Writer，仅输出正文内容。

    - 通过 ``filter_settings_spec`` 精简可用设置；
    - 在 ``apply_template`` 中返回 ``{body}``，避免包裹多余模板结构。
    """
    settings_spec = filter_settings_spec(
        Writer.settings_spec,
        "template",
    )

    def apply_template(self):
        """使用插值字典仅渲染 `body` 段并返回字符串。"""
        subs = self.interpolation_dict()
        return "{body}\n".format(**subs)

    def __init__(self):
        """初始化写入器，设置部件存储与翻译器类型。"""
        self.parts = {}
        self.translator_class = SimpleTranslator


def convert(input_config: str, input_myst: str, writer_name: str) -> dict:
    """将 MyST 文本转换为指定输出格式。

    Args:
        input_config: YAML 字符串形式的 Docutils 设置（可为空）。
        input_myst: 待转换的 MyST 文本内容。
        writer_name: 输出目标；包含 ``html`` 时使用 ``SimpleWriter``，
            否则传递给 Docutils 的 ``writer_name``。

    Returns:
        dict: 包含 ``output``（转换结果字符串）与 ``warnings``（警告文本）。

    Notes:
        - 配置解析失败时会记录错误并回退到空设置；
        - 通过 ``publish_string`` 执行转换，异常会被捕获并返回堆栈信息。
    """
    warning_stream = StringIO()
    try:
        settings = yaml.safe_load(input_config) if input_config else {}
        assert isinstance(settings, dict), "not a dictionary"
    except Exception as exc:
        warning_stream.write(f"ERROR: config load: {exc}\n")
        settings = {}
    settings.update(
        {
            "output_encoding": "unicode",
            "warning_stream": warning_stream,
            # to mimic the sphinx parser
            "doctitle_xform": False,
            "sectsubtitle_xform": False,
            "initial_header_level": 1,
        }
    )
    try:
        output = publish_string(
            input_myst,
            parser=PARSER,
            settings_overrides=settings,
            **(
                {"writer": SimpleWriter()}
                if is_html_format((writer_name or "").lower())
                else {"writer_name": writer_name}
            ),
        )
    except Exception as exc:
        output = f"ERROR: conversion:\n{exc}\n{traceback.format_exc()}"
    return {"output": output, "warnings": warning_stream.getvalue()}


# 使用 dataclass 统一管理 DOM 引用
@dataclass
class LivePreviewDOM:
    version_label: object = None
    config_textarea: object = None
    input_textarea: object = None
    output_iframe: object = None
    output_raw: object = None
    warnings_textarea: object = None
    oformat_select: object = None

DOM = LivePreviewDOM()


def do_convert(event=None):
    """读取页面输入并触发转换，更新预览与原始输出。

    - 当输出格式包含 `html` 时，将 HTML 注入到预览容器；
    - 否则提示切换到 HTML 以查看渲染结果；
    - 同步展示转换产生的警告信息。
    """
    from js import window
    global _last_run_ms, _last_config, _last_input, _last_format
    # Ensure required DOM elements exist
    if not all([DOM.config_textarea, DOM.input_textarea, DOM.output_raw, DOM.output_iframe, DOM.warnings_textarea, DOM.oformat_select]):
        try:
            window.console.warn("live_preview: missing required DOM elements")
        except Exception:
            pass
        return

    curr_config = DOM.config_textarea.value or ""
    curr_input = DOM.input_textarea.value or ""
    curr_format = DOM.oformat_select.value or ""
    changed = (curr_config != _last_config) or (curr_input != _last_input) or (curr_format != _last_format)

    # Simple throttle to avoid excessive conversions during rapid typing
    try:
        now = window.performance.now()
    except Exception:
        now = 0
    if changed and (now - _last_run_ms < MIN_INTERVAL_MS):
        return

    result = convert(curr_config, curr_input, curr_format)
    _last_run_ms = now
    _last_config, _last_input, _last_format = curr_config, curr_input, curr_format

    DOM.output_raw.value = result["output"]
    if is_html_format(curr_format):
        DOM.output_iframe.innerHTML = result["output"]
    else:
        DOM.output_iframe.textContent = "Change output format to HTML to see output"
    DOM.warnings_textarea.value = result["warnings"]

def setup_dom():
    """初始化浏览器端的 DOM 引用与事件绑定，并进行首轮转换。"""
    from js import document
    # 通过 document 查询并缓存需要的元素到 DOM 容器
    DOM.version_label = document.querySelector("span#myst-version")
    DOM.config_textarea = document.querySelector("textarea#input_config")
    DOM.input_textarea = document.querySelector("textarea#input_myst")
    DOM.output_iframe = document.querySelector("div#output_html")
    DOM.output_raw = document.querySelector("textarea#output_raw")
    DOM.warnings_textarea = document.querySelector("textarea#output_warnings")
    DOM.oformat_select = document.querySelector("select#output_format")

    # 设置版本标签与事件处理
    if DOM.version_label:
        DOM.version_label.textContent = f"myst-parser v{__version__}"
    if DOM.config_textarea:
        DOM.config_textarea.oninput = do_convert
    if DOM.input_textarea:
        DOM.input_textarea.oninput = do_convert
    if DOM.oformat_select:
        DOM.oformat_select.onchange = do_convert

    # 首次渲染
    do_convert()

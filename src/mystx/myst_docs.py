"""把 ``myst_parser._docs`` 自带的文档工具指令注册到 Sphinx 项目。

上游没有公开注册入口，其文档站直接在 ``conf.py`` 里逐条 ``add_directive``。
本模块把该段收拢为 :func:`register_docs_directives`，并把示例指令的三个
CSS 类名参数化：``<prefix>`` / ``<prefix>-source`` / ``<prefix>-render``。
"""

import importlib
from typing import Any

from sphinx.application import Sphinx

#: 示例指令的默认类名前缀，与 mystx 文档的 ``local.css`` 契约一致。
DEFAULT_EXAMPLE_PREFIX = "myst-example"

#: ``(指令名, 上游符号名, 是否包装为示例指令)``——注册顺序即最终顺序。
#: 指令名列表由本表派生，不再维护第二份名单。
_DIRECTIVE_SPEC: tuple[tuple[str, str, bool], ...] = (
    ("myst-config", "MystConfigDirective", False),
    ("docutils-cli-help", "DocutilsCliHelpDirective", False),
    ("doc-directive", "DirectiveDoc", False),
    ("myst-warnings", "MystWarningsDirective", False),
    ("myst-example", "SyntaxExampleDocsDirective", True),
    ("myst-admonitions", "MystAdmonitionDirective", False),
    ("myst-to-html", "MystToHTMLDirective", False),
)

#: 默认注册的指令名，供文档或测试引用（顺序与注册顺序一致）。
DOCS_DIRECTIVE_NAMES: tuple[str, ...] = tuple(
    name for name, _, _ in _DIRECTIVE_SPEC
)


def example_classes(prefix: str = DEFAULT_EXAMPLE_PREFIX) -> tuple[str, str, str]:
    """由前缀派生示例指令的三个容器类名 ``(wrapper, source, render)``。"""
    return prefix, f"{prefix}-source", f"{prefix}-render"


def make_example_directive(
    prefix: str = DEFAULT_EXAMPLE_PREFIX,
    *,
    base: type | None = None,
) -> type:
    """构造「源码／渲染双栏示例」指令类，仅重写三个 CSS 类名。

    渲染语义（双栏、无标题、sphinx-design 容器）全部沿用上游
    ``SyntaxExampleDocsDirective``；本函数只把类名钉到调用方契约上。

    Args:
        prefix: 类名前缀，默认 ``"myst-example"``。
        base: 基类，默认惰性导入的 ``SyntaxExampleDocsDirective``；
            显式传入便于测试或替换上游实现。
    """
    if base is None:
        from myst_parser._docs import SyntaxExampleDocsDirective as base  # noqa: N813

    wrapper, source, render = example_classes(prefix)
    return type(
        "MystExampleDirective",
        (base,),
        {
            "wrapper_classes": (wrapper,),
            "source_classes": (source,),
            "render_classes": (render,),
        },
    )


def _resolve_directives(upstream: Any, example_prefix: str) -> dict[str, Any]:
    """按 ``_DIRECTIVE_SPEC`` 从上游模块取出指令类，示例指令就地包装。"""
    directives: dict[str, Any] = {}
    for name, symbol, wrap_example in _DIRECTIVE_SPEC:
        directive = getattr(upstream, symbol)
        directives[name] = (
            make_example_directive(example_prefix, base=directive)
            if wrap_example
            else directive
        )
    return directives


def _load_upstream() -> Any:
    """导入上游文档工具模块；模块缺失时给出可执行的安装提示。"""
    try:
        return importlib.import_module("myst_parser._docs")
    except ImportError as exc:
        raise ImportError(
            "myst_parser._docs 不可用（需要 myst-parser>=5.1）："
            f"{exc}。请安装 mystx[doc] 或 `pip install \"myst-parser>=5.1\"`。"
        ) from exc


def register_docs_directives(
    app: Sphinx,
    *,
    example_prefix: str = DEFAULT_EXAMPLE_PREFIX,
    register_transforms: bool = True,
    register_lexer: bool = True,
) -> None:
    """注册 MyST 文档工具指令、后置变换与词法器。

    依赖 ``myst_parser >= 5.1`` 与 ``sphinx-syntax-example >= 0.2.0``：前者提供
    ``myst_parser._docs`` 模块本体，后者提供其中被硬导入的
    ``SyntaxExampleDocsDirective``（上游未在依赖清单声明该包）。模块或符号缺失
    时抛出带安装提示的 :class:`ImportError`，并保留原始异常供排查。
    """
    upstream = _load_upstream()
    try:
        directives = _resolve_directives(upstream, example_prefix)
        transforms = (upstream.StripUnsupportedLatex, upstream.NumberSections)
        lexer = upstream.MystLexer
    except AttributeError as exc:
        raise ImportError(
            "myst_parser._docs 缺少预期符号（文档依赖未装全）："
            f"{exc}。请安装 mystx[doc] 或 "
            '`pip install "myst-parser>=5.1" "sphinx-syntax-example>=0.2.0"`。'
        ) from exc

    for name, directive in directives.items():
        app.add_directive(name, directive)
    if register_transforms:
        for transform in transforms:
            app.add_post_transform(transform)
    if register_lexer:
        app.add_lexer("myst", lexer)

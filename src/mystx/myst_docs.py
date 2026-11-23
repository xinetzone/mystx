"""把 ``myst_parser._docs`` 自带的文档工具指令注册到 Sphinx 项目。

``myst_parser._docs`` 内部实现了一批「用文档说明 MyST 自身」的指令、
后置变换与词法器，但没有提供公开的注册入口——上游自己的文档站直接在
``conf.py`` 的 ``setup()`` 里逐条 ``app.add_directive(...)``。任何想要
展示 MyST 配置项、告警清单或「源码／渲染双栏示例」的项目都得复制这一段。

本模块把该段收拢为 :func:`register_docs_directives`，并把示例指令的
三个 CSS 类名参数化：下游只需给出类名前缀，即可让样式表继续作用于
``<prefix>`` / ``<prefix>-source`` / ``<prefix>-render`` 三个容器。
"""

from typing import Any

from sphinx.application import Sphinx

#: 示例指令的默认类名前缀，与 mystx 文档的 ``local.css`` 契约一致。
DEFAULT_EXAMPLE_PREFIX = "myst-example"

#: 默认注册的指令名，供文档或测试引用（顺序与注册顺序一致）。
DOCS_DIRECTIVE_NAMES: tuple[str, ...] = (
    "myst-config",
    "docutils-cli-help",
    "doc-directive",
    "myst-warnings",
    "myst-example",
    "myst-admonitions",
    "myst-to-html",
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


def register_docs_directives(
    app: Sphinx,
    *,
    example_prefix: str = DEFAULT_EXAMPLE_PREFIX,
    register_transforms: bool = True,
    register_lexer: bool = True,
) -> None:
    """注册 MyST 文档工具指令、后置变换与词法器。

    依赖 ``myst_parser >= 5.1``（``myst_parser._docs`` 在该版本提供
    上述符号）；未安装时抛出带安装提示的 :class:`ImportError`。

    Args:
        app: Sphinx 应用实例。
        example_prefix: 示例指令的 CSS 类名前缀。
        register_transforms: 是否同时注册 ``StripUnsupportedLatex`` /
            ``NumberSections`` 两个后置变换。
        register_lexer: 是否同时注册 ``myst`` 词法器。
    """
    try:
        from myst_parser._docs import (
            DirectiveDoc,
            DocutilsCliHelpDirective,
            MystAdmonitionDirective,
            MystConfigDirective,
            MystLexer,
            MystToHTMLDirective,
            MystWarningsDirective,
            NumberSections,
            StripUnsupportedLatex,
            SyntaxExampleDocsDirective,
        )
    except ImportError as exc:  # pragma: no cover - 由缺依赖触发
        raise ImportError(
            "myst_parser._docs 不可用：请安装 myst-parser>=5.1 后重试。"
        ) from exc

    directives: dict[str, Any] = {
        "myst-config": MystConfigDirective,
        "docutils-cli-help": DocutilsCliHelpDirective,
        "doc-directive": DirectiveDoc,
        "myst-warnings": MystWarningsDirective,
        "myst-example": make_example_directive(example_prefix, base=SyntaxExampleDocsDirective),
        "myst-admonitions": MystAdmonitionDirective,
        "myst-to-html": MystToHTMLDirective,
    }
    for name, directive in directives.items():
        app.add_directive(name, directive)

    if register_transforms:
        app.add_post_transform(StripUnsupportedLatex)
        app.add_post_transform(NumberSections)
    if register_lexer:
        app.add_lexer("myst", MystLexer)

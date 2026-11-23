"""契约测试：``myst_fence_as_directive`` 的每个围栏都必须有对应扩展负责注册指令。

历史缺陷：``defaults.py`` 把 ``mermaid`` 围栏映射为 ``mermaid`` 指令，但
``extensions.py`` 以「不在依赖中」为由注释掉了 ``sphinxcontrib.mermaid``，
形成死映射——一旦文档出现 ```mermaid 围栏，构建期会因指令未注册而失败。
"""
from mystx.config.defaults import DEFAULT_MYST_CONFIG
from mystx.extensions import DEFAULT_OPTIONAL_EXTENSIONS

# 围栏名 -> 提供同名指令的扩展
_FENCE_PROVIDERS = {
    "mermaid": "sphinxcontrib.mermaid",
}


def test_each_fence_directive_has_provider_extension():
    fences = DEFAULT_MYST_CONFIG.get("myst_fence_as_directive", [])
    missing = [
        f"{fence}->{ext}"
        for fence in fences
        if (ext := _FENCE_PROVIDERS.get(fence)) and ext not in DEFAULT_OPTIONAL_EXTENSIONS
    ]
    assert missing == [], f"围栏指令缺少装配扩展：{missing}"

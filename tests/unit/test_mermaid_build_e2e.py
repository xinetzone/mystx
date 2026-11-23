"""端到端：含 ```mermaid 围栏的最小文档在 mystx 预设下可成功构建。

覆盖三层契约：

1. ``DEFAULT_OPTIONAL_EXTENSIONS`` 收录 ``sphinxcontrib.mermaid`` 且可被
   :func:`mystx.resolve_extensions` 解析（防止常量与装配清单脱节）；
2. ``myst_fence_as_directive = ["mermaid"]`` 的围栏被转换为 ``mermaid`` 指令，
   doctree 中出现对应节点而非普通 code 块；
3. HTML 输出中出现 mermaid 容器，说明渲染链完整。

构建在独立子进程中执行：同进程内多次 ``Sphinx(...)`` 会相互污染注册表与
环境（实测出现 ``KeyError: 'myst-nb'``），隔离进程可获得确定结果。
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

_PROBE = r"""
import json
import sys
from pathlib import Path

from sphinx.application import Sphinx

src, out, doctrees = (Path(p) for p in sys.argv[1:4])
app = Sphinx(
    srcdir=str(src),
    confdir=str(src),
    outdir=str(out),
    doctreedir=str(doctrees),
    buildername="html",
    freshenv=True,
    warningiserror=False,
    verbosity=0,
)
app.build()

doctree = app.env.get_doctree("index")
codes = [n["code"] for n in doctree.findall() if n.tagname == "mermaid"]
html = (out / "index.html").read_text(encoding="utf-8")
print(
    "PROBE="
    + json.dumps(
        {
            "extensions": sorted(app.extensions),
            "codes": codes,
            "has_mermaid_container": 'class="mermaid"' in html,
        }
    )
)
"""


@pytest.fixture(scope="module")
def mermaid_build():
    tmp = Path(tempfile.mkdtemp(prefix="mystx_mermaid_"))
    src = tmp / "src"
    out = tmp / "out"
    doctrees = tmp / "doctrees"
    src.mkdir()
    out.mkdir()
    doctrees.mkdir()

    source_root = Path(__file__).resolve().parents[2] / "src"
    conf = f'''
import sys
if {str(source_root)!r} not in sys.path:
    sys.path.insert(0, {str(source_root)!r})

from mystx.presets import build_minimal_myst_config

globals().update(
    build_minimal_myst_config(
        {{
            "project": "mystx-mermaid-e2e",
            "extensions_optional": ("sphinxcontrib.mermaid",),
            # 本用例只关心围栏→指令→HTML 链路，避免书系主题的头部按钮依赖
            "html_theme": "alabaster",
            "config_override": {{"html_static_path": []}},
        }}
    )
)
'''
    (src / "conf.py").write_text(conf, encoding="utf-8")
    (src / "index.md").write_text(
        "# Mermaid\n\n```mermaid\ngraph TD;\n    A-->B;\n```\n",
        encoding="utf-8",
    )
    probe = tmp / "probe.py"
    probe.write_text(_PROBE, encoding="utf-8")

    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        filter(None, [str(source_root), env.get("PYTHONPATH", "")])
    )
    proc = subprocess.run(
        [sys.executable, str(probe), str(src), str(out), str(doctrees)],
        capture_output=True,
        text=True,
        env=env,
        timeout=120,
    )
    lines = [ln for ln in proc.stdout.splitlines() if ln.startswith("PROBE=")]
    assert lines, f"子进程构建未产出结果：\n{proc.stdout}\n{proc.stderr}"

    yield json.loads(lines[-1][len("PROBE=") :])
    shutil.rmtree(tmp, ignore_errors=True)


def test_default_optional_extensions_contains_mermaid():
    from mystx.extensions import DEFAULT_OPTIONAL_EXTENSIONS, resolve_extensions

    assert "sphinxcontrib.mermaid" in DEFAULT_OPTIONAL_EXTENSIONS
    assert "sphinxcontrib.mermaid" in resolve_extensions(
        optional=DEFAULT_OPTIONAL_EXTENSIONS
    )


def test_mermaid_extension_is_assembled(mermaid_build):
    assert "sphinxcontrib.mermaid" in mermaid_build["extensions"]


def test_mermaid_fence_becomes_directive_node(mermaid_build):
    codes = mermaid_build["codes"]
    assert codes, "围栏未被转换为 mermaid 指令节点"
    assert "A-->B" in codes[0]


def test_mermaid_fence_renders_html(mermaid_build):
    assert mermaid_build["has_mermaid_container"], "输出中缺少 mermaid 容器"

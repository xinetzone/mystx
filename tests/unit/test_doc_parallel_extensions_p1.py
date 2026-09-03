"""集成测试：验证 mystx 文档构建所用的扩展清单在 Sphinx parallel=N 模式下
全部显式声明 `parallel_read_safe=True` 且 `parallel_write_safe=True`，
确保 Fail-Fast 钩子不会误触发，并阻断将来新增未声明扩展导致的静默串行退化。

来源：P1-A 审计 (sphinx-parallel-build-5k-scale-20260903 报告)。
"""
from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

import pytest

# 需要的 20 项扩展（mystx 文档真实启用 + 自动注入项）
TARGET_EXTS: tuple[str, ...] = (
    "mystx",
    "mystx.ext.github_readme_stats",
    "myst_parser",
    "sphinx_design",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.graphviz",
    "sphinx.ext.extlinks",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.mathjax",
    "sphinx_copybutton",
    "sphinx_comments",
    "sphinx_sitemap",
    "sphinxcontrib.bibtex",
    "sphinx_contributors",
    "sphinxext.opengraph",
    "sphinx_tippy",
    "sphinx_examples",
    "sphinx_pyscript",
)


@pytest.fixture
def sphinx_app_parallel4():
    """以 mystx 文档真实扩展清单 + parallel=4 启动最小 Sphinx app."""
    from sphinx.application import Sphinx

    tmp = Path(tempfile.mkdtemp(prefix="mystx_p1_parallel_"))
    src = tmp / "src"
    out = tmp / "out"
    dochtml = tmp / "doctrees"
    src.mkdir()
    out.mkdir()
    dochtml.mkdir()

    # 注入当前 src 源码路径（同 conftest 模式）
    _SRC = Path(__file__).resolve().parents[2] / "src"
    conf = f'''
import sys
if {str(_SRC)!r} not in sys.path:
    sys.path.insert(0, {str(_SRC)!r})

extensions = [
    "mystx",
    "sphinx_design",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx_comments",
    "sphinx_sitemap",
    "sphinxcontrib.bibtex",
    "sphinx.ext.graphviz",
    "sphinx_contributors",
    "sphinxext.opengraph",
    "sphinx_tippy",
    "sphinx.ext.extlinks",
    "sphinx_examples",
    "sphinx_pyscript",
    "mystx.ext.github_readme_stats",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
]
html_baseurl = "https://example.org/"
bibtex_bibfiles = []
project = "mystx-p1-parallel-check"
'''
    (src / "conf.py").write_text(conf, encoding="utf-8")
    (src / "index.md").write_text("# Hi\n\nhello world\n", encoding="utf-8")

    app = Sphinx(
        srcdir=str(src),
        confdir=str(src),
        outdir=str(out),
        doctreedir=str(dochtml),
        buildername="html",
        parallel=0,
        freshenv=True,
        warningiserror=False,
        verbosity=0,
    )
    app.parallel = 4
    yield app

    shutil.rmtree(tmp, ignore_errors=True)


def test_all_target_extensions_loaded(sphinx_app_parallel4):
    missing = [e for e in TARGET_EXTS if e not in sphinx_app_parallel4.extensions]
    assert missing == [], f"存在未加载的预期扩展（请同步更新本清单与 conf.py）：{missing}"


def test_is_parallel_allowed_read_and_write(sphinx_app_parallel4):
    """核心断言：Fail-Fast 钩子不会在 parallel=4 时被误触发。"""
    assert sphinx_app_parallel4.is_parallel_allowed("read") is True, (
        "Fail-Fast 断言将触发：至少 1 个扩展的 parallel_read_safe 非 True。"
        " 请运行 P1 审计找出阻塞扩展后，更新其 setup() 返回值或"
        " 在 conf.py setup() 中覆写其 app.extensions[name].parallel_read_safe。"
    )
    assert sphinx_app_parallel4.is_parallel_allowed("write") is True, (
        "Write 阶段退化串行：至少 1 个扩展的 parallel_write_safe 非 True。"
    )


def test_each_extension_parallel_metadata(sphinx_app_parallel4):
    """逐扩展断言 parallel_*_safe 真值，错误消息里直接指出未通过的扩展名。"""
    bad_read: list[str] = []
    bad_write: list[str] = []
    for name in TARGET_EXTS:
        ext = sphinx_app_parallel4.extensions[name]
        pr = getattr(ext, "parallel_read_safe", None)
        pw = getattr(ext, "parallel_write_safe", None)
        if pr is not True:
            bad_read.append(f"{name}(={pr!r})")
        if pw is not True:
            bad_write.append(f"{name}(={pw!r})")
    assert bad_read == [], f"parallel_read_safe != True 的扩展：{bad_read}"
    assert bad_write == [], f"parallel_write_safe != True 的扩展：{bad_write}"

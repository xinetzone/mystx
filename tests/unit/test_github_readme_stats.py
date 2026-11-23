"""GitHub Readme Stats 指令的 HTML 转义与 URL 拼装契约。"""
from __future__ import annotations

from docutils import nodes

from mystx.ext.github_readme_stats.base import BaseGitHubCardDirective
from mystx.ext.github_readme_stats.pinned_repo import GitHubPinnedRepoDirective


class _Reporter:
    def error(self, msg, line=None):
        return nodes.error("", nodes.paragraph("", msg))


class _StateMachine:
    reporter = _Reporter()


def _make(directive_cls, options=None, state_machine=None):
    return directive_cls(
        "github-pinned-repo",
        [],
        options or {},
        [],
        1,
        0,
        "",
        None,
        state_machine or _StateMachine(),
    )


def test_build_url_serializes_flags_and_drops_empty_values():
    url = _make(BaseGitHubCardDirective).build_url(
        "http://api/pin",
        {"username": "a b", "theme": "dark", "show_owner": True, "hide": False, "empty": ""},
    )

    assert url.startswith("http://api/pin?")
    assert "username=a+b" in url
    assert "show_owner=True" in url
    assert "hide" not in url and "empty" not in url


def test_create_image_node_escapes_src_and_alt():
    node = _make(BaseGitHubCardDirective).create_image_node(
        "http://x/?a=1&c=<d>", alt="Pi<ned"
    )

    assert isinstance(node, nodes.raw)
    html = node.astext()
    assert 'src="http://x/?a=1&amp;c=&lt;d&gt;"' in html
    assert 'alt="Pi&lt;ned"' in html
    assert "<a " not in html, "未提供 link 时不应生成 <a> 包裹"


def test_create_image_node_escapes_link():
    node = _make(BaseGitHubCardDirective).create_image_node(
        "http://img", "Pinned Repo", link='http://l/?x="y"&z=<w>'
    )

    html = node.astext()
    assert html.startswith('<a href="http://l/?x=&quot;y&quot;&amp;z=&lt;w&gt;">')
    assert html.endswith("</a>")


def test_pinned_repo_builds_pin_url_and_wraps_link():
    directive = _make(
        GitHubPinnedRepoDirective,
        {"username": "octo cat", "repo": "re<po>", "theme": "dark", "link": "http://l/"},
    )

    result = directive.run()

    html = result[0].astext()
    assert "api/pin?username=octo+cat&amp;repo=re%3Cpo%3E&amp;theme=dark" in html
    assert 'href="http://l/"' in html
    assert 'alt="Pinned Repo"' in html


def test_pinned_repo_reports_missing_required_options():
    result = _make(GitHubPinnedRepoDirective).run()

    assert len(result) == 1
    assert ":username:" in result[0].astext() and ":repo:" in result[0].astext()

from mystx.ext.github_readme_stats.base import BaseGitHubCardDirective


def test_build_url_basic():
    d = BaseGitHubCardDirective()
    url = d.build_url(
        "https://example/api",
        {"username": "octocat", "theme": "dark", "show_icons": True},
    )
    assert "username=octocat" in url
    assert "theme=dark" in url
    assert "show_icons=True" in url


def test_build_url_omit_empty():
    d = BaseGitHubCardDirective()
    url = d.build_url("https://example/api", {"hide": "", "repo": None})
    assert url.endswith("https://example/api?") is False
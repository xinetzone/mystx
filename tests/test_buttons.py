"""页眉按钮数据测试：URL 规则与缺数据降级。"""

from mystx.book.buttons import build_buttons

FLAGS = ["download", "fullscreen", "source", "edit", "issue", "repo"]


def base_context():
    return {
        "sourcename": "guide/setup.rst.txt",
        "page_source_suffix": ".rst",
        "doc_path": "doc",
    }


def types(buttons):
    return [button["type"] for button in buttons]


def test_without_repo_only_local_buttons():
    buttons = build_buttons("guide/setup", base_context(), FLAGS)
    assert [b["label"] for b in buttons] == ["Download this page", "Fullscreen mode"]
    assert build_buttons("guide/setup", base_context(), ["repo", "edit"]) == []


def test_download_requires_sourcename():
    context = base_context()
    context.pop("sourcename")
    assert build_buttons("guide/setup", context, ["download"]) == []


def test_github_urls():
    context = base_context()
    context.update(
        github_user="acme",
        github_repo="docs",
        github_version="main",
    )
    by_label = {b["label"]: b["href"] for b in build_buttons("guide/setup", context, FLAGS) if "href" in b}
    assert by_label["Source repository"] == "https://github.com/acme/docs"
    assert by_label["Suggest edit"] == "https://github.com/acme/docs/edit/main/doc/guide/setup.rst"
    assert by_label["View source"] == "https://github.com/acme/docs/blob/main/doc/guide/setup.rst?plain=1"
    assert by_label["Open an issue"].startswith("https://github.com/acme/docs/issues/new")


def test_gitlab_uses_dash_paths():
    context = base_context()
    context.update(gitlab_user="acme", gitlab_repo="docs", gitlab_version="main")
    by_label = {b["label"]: b["href"] for b in build_buttons("guide/setup", context, FLAGS) if "href" in b}
    assert by_label["Suggest edit"] == "https://gitlab.com/acme/docs/-/edit/main/doc/guide/setup.rst"
    assert by_label["View source"] == "https://gitlab.com/acme/docs/-/blob/main/doc/guide/setup.rst?plain=1"


def test_bitbucket_source_has_no_plain_query():
    context = base_context()
    context.update(bitbucket_user="acme", bitbucket_repo="docs", bitbucket_version="main")
    by_label = {b["label"]: b["href"] for b in build_buttons("guide/setup", context, FLAGS) if "href" in b}
    assert by_label["View source"] == "https://bitbucket.org/acme/docs/src/main/doc/guide/setup.rst"


def test_custom_provider_base():
    context = base_context()
    context.update(github_user="acme", github_repo="docs", github_version="dev", github_url="https://ghe.example.com")
    buttons = build_buttons("index", context, ["repo"])
    assert buttons[0]["href"] == "https://ghe.example.com/acme/docs"


def test_order_follows_configuration():
    context = base_context()
    buttons = build_buttons("index", context, ["fullscreen", "download"])
    assert [b["label"] for b in buttons] == ["Fullscreen mode", "Download this page"]

from .stats import GitHubStatsDirective
from .top_langs import GitHubTopLangsDirective
from .pinned_repo import GitHubPinnedRepoDirective

def setup(app):
    app.add_directive("github-stats", GitHubStatsDirective)
    app.add_directive("github-top-langs", GitHubTopLangsDirective)
    app.add_directive("github-pinned-repo", GitHubPinnedRepoDirective)
    return {"version": "0.1", "parallel_read_safe": True}

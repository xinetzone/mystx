import json
from pathlib import Path


def file_stats(root: Path, patterns: tuple[str, ...]) -> dict:
    files = []
    for pat in patterns:
        files.extend(root.rglob(pat))
    total_size = sum(p.stat().st_size for p in files)
    return {
        "count": len(files),
        "total_bytes": total_size,
        "files": [str(p.relative_to(root)) for p in files],
    }


def main() -> None:
    base = Path(__file__).resolve().parents[2] / "src" / "mystx" / "theme" / "mystx"
    static = base / "static"
    assets = base / "assets"

    report = {
        "static": {
            "css": file_stats(static, ("css/*.css",)),
            "js": file_stats(static, ("js/*.js",)),
            "images": file_stats(static, ("images/*",)),
        },
        "assets": {
            "css": file_stats(assets, ("css/*.css",)) if assets.exists() else None,
            "js": file_stats(assets, ("js/*.js",)) if assets.exists() else None,
            "images": file_stats(assets, ("images/*",)) if assets.exists() else None,
        },
    }

    out_dir = Path(__file__).parent / ".." / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "perf-report.json").write_text(json.dumps(report, indent=2), "utf-8")


if __name__ == "__main__":
    main()
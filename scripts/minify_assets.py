from pathlib import Path


def minify_css(text: str) -> str:
    return "".join(line.strip() for line in text.splitlines() if not line.strip().startswith("/*"))


def minify_js(text: str) -> str:
    return "".join(line.strip() for line in text.splitlines() if not line.strip().startswith("//"))


def write_minified(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(src.read_text("utf-8"), "utf-8")


def main() -> None:
    base = Path(__file__).resolve().parents[2] / "src" / "mystx" / "theme" / "mystx"
    static = base / "static"
    assets = base / "assets"
    for css in static.glob("css/*.css"):
        out = assets / "css" / css.name
        out.write_text(minify_css(css.read_text("utf-8")), "utf-8")
    for js in static.glob("js/*.js"):
        out = assets / "js" / js.name
        out.write_text(minify_js(js.read_text("utf-8")), "utf-8")


if __name__ == "__main__":
    main()
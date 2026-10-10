"""draws langs.svg, the language pills and donut for the profile readme"""
import json
import os
import urllib.request

USER = "nchiamsachang"
TOP = 5
MIN_PERCENT = 0.5   # smaller shares are left out

# repos left out of the numbers
SKIP_REPOS = {"nchiamsachang", "test1", "github-chapter-2-sandbox"}
# build files and editor boilerplate
SKIP_LANGS = {"Batchfile", "CMake", "Visual Basic .NET"}

COLOURS = {
    "C++": "#f34b7d", "C#": "#3fb950", "Python": "#58a6ff", "HTML": "#e34c26",
    "PHP": "#8892bf", "JavaScript": "#f1e05a", "Java": "#d29922", "C": "#8b949e",
    "CSS": "#a371f7",
}
FALLBACK = "#8b949e"

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "langs.svg")
SANS = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"


def get(url):
    """one github api call, parsed"""
    headers = {"User-Agent": USER, "Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = "bearer " + token
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as response:
        return json.load(response)


def fetch_repo_languages(user):
    """bytes per language for each of the user's own repos"""
    repos = get("https://api.github.com/users/%s/repos?per_page=100" % user)
    result = {}
    for repo in repos:
        if repo["fork"] or repo["name"] in SKIP_REPOS:
            continue
        sizes = get(repo["languages_url"])
        sizes = {lang: size for lang, size in sizes.items() if lang not in SKIP_LANGS}
        if sizes:
            result[repo["name"]] = sizes
    return result


def shares(repo_languages):
    """percent per language, each repo weighted equally, largest first"""
    totals = {}
    for sizes in repo_languages.values():
        repo_total = sum(sizes.values())
        for lang, size in sizes.items():
            totals[lang] = totals.get(lang, 0) + size / repo_total
    count = len(repo_languages)
    ranked = sorted(totals.items(), key=lambda item: item[1], reverse=True)
    percents = [(lang, share / count * 100) for lang, share in ranked]
    return [(lang, percent) for lang, percent in percents if percent >= MIN_PERCENT]


def pills(names, left, top, width):
    """pill tags wrapped into rows, as svg text"""
    parts = []
    x, y = left, top
    for name in names:
        colour = COLOURS.get(name, FALLBACK)
        w = 34 + len(name) * 7.6
        if x + w > left + width:
            x, y = left, y + 36
        parts.append(
            f'<rect x="{x:.0f}" y="{y}" width="{w:.0f}" height="26" rx="13" fill="{colour}" fill-opacity="0.15" stroke="{colour}" stroke-opacity="0.45"/>'
            f'<circle cx="{x + 14:.0f}" cy="{y + 13}" r="4" fill="{colour}"/>'
            f'<text x="{x + 24:.0f}" y="{y + 17.5}" fill="{colour}" font-family="{SANS}" font-size="13">{name}</text>'
        )
        x += w + 8
    return "\n".join(parts)


def donut(top, cx, cy, radius):
    """ring segments for the top languages, as svg text"""
    around = 2 * 3.14159265 * radius
    total = sum(share for _, share in top)
    parts = []
    start = 0.0
    for name, share in top:
        length = share / total * around
        parts.append(
            f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="{COLOURS.get(name, FALLBACK)}" stroke-width="16" '
            f'stroke-dasharray="{length:.2f} {around - length:.2f}" stroke-dashoffset="{-start:.2f}" transform="rotate(-90 {cx} {cy})"/>'
        )
        start += length
    return "\n".join(parts)


def legend(top, x, y):
    """name and percent rows, as svg text"""
    parts = []
    for i, (name, share) in enumerate(top):
        row = y + i * 26
        parts.append(
            f'<circle cx="{x}" cy="{row - 4}" r="5" fill="{COLOURS.get(name, FALLBACK)}"/>'
            f'<text x="{x + 14}" y="{row}" fill="#e6edf3" font-family="{SANS}" font-size="13">{name}</text>'
            f'<text x="646" y="{row}" fill="#8b949e" font-family="{SANS}" font-size="13" text-anchor="end">{share:.0f}%</text>'
        )
    return "\n".join(parts)


def draw(ranked, repo_count):
    """the whole card as svg text"""
    top = ranked[:TOP]
    names = [name for name, _ in ranked]
    summary = ", ".join("%s %.0f%%" % (name, share) for name, share in top)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 680 220" width="680" height="220" role="img" aria-labelledby="title desc">
<title id="title">Languages used by {USER}</title>
<desc id="desc">Share of each language across {repo_count} repositories: {summary}.</desc>
<rect x="0.5" y="0.5" width="329" height="219" rx="12" fill="#0d1117" stroke="#30363d"/>
<rect x="350.5" y="0.5" width="329" height="219" rx="12" fill="#0d1117" stroke="#30363d"/>
<text x="24" y="36" fill="#8b949e" font-family="{SANS}" font-size="12" font-weight="600" letter-spacing="1">CORE TECHNOLOGIES</text>
{pills(names, 24, 56, 290)}
{donut(top, 426, 100, 48)}
<text x="426" y="104" fill="#8b949e" font-family="{SANS}" font-size="12" text-anchor="middle">{len(names)} langs</text>
{legend(top, 506, 54)}
<text x="374" y="200" fill="#8b949e" font-family="{SANS}" font-size="11">Based on {repo_count} repos, each weighted equally</text>
</svg>
"""


def main():
    repo_languages = fetch_repo_languages(USER)
    ranked = shares(repo_languages)
    with open(OUTPUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(draw(ranked, len(repo_languages)))
    print("wrote langs.svg from %d repos: %s" % (
        len(repo_languages), ", ".join("%s %.0f%%" % item for item in ranked)))


if __name__ == "__main__":
    main()

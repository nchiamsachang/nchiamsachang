"""draws one project card per repo into cards/ for the profile readme"""
# run again after editing PROJECTS
import os
import textwrap

# repo, title, language, description
PROJECTS = [
    ("tcg-tournament-manager", "TCG Tournament Manager", "C++",
     "Desktop app for running trading card game tournaments, with regression and UI test suites"),
    ("Steam-Recommender-System-Linear-Algebra", "Steam Game Recommender", "Python",
     "Game recommendations built on 41 million Steam reviews"),
    ("Game-Engine-Simulation-Benchmark", "Game Engine Benchmark", "C#",
     "The same game-engine update loop in C# and Python, with shared boundary tests"),
    ("First-store-Web-Technologies", "E-Book Storefront", "PHP",
     "E-book store with a JavaScript cart and PHP/MySQL checkout"),
]

COLOURS = {"C++": "#f34b7d", "C#": "#3fb950", "Python": "#58a6ff", "PHP": "#8892bf"}

FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cards")
SANS = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"


def card(title, language, description):
    """one card as svg text"""
    colour = COLOURS.get(language, "#8b949e")
    pill_width = 22 + len(language) * 7.6
    pill_x = 316 - pill_width
    lines = textwrap.wrap(description, 44)[:3]
    text = "".join(
        f'<text x="20" y="{70 + i * 20}" fill="#c9d1d9" font-family="{SANS}" font-size="13">{line.replace("&", "&amp;")}</text>'
        for i, line in enumerate(lines)
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 336 130" width="336" height="130" role="img" aria-label="{title}: {description}">
<rect x="0.5" y="0.5" width="335" height="129" rx="12" fill="#0d1117" stroke="#30363d"/>
<g transform="translate(20,20) scale(0.75)" fill="none" stroke="#8b949e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/></g>
<text x="46" y="35" fill="#3fb950" font-family="{SANS}" font-size="16" font-weight="600">{title}</text>
<rect x="{pill_x:.0f}" y="18" width="{pill_width:.0f}" height="22" rx="11" fill="{colour}" fill-opacity="0.15"/>
<text x="{pill_x + pill_width / 2:.0f}" y="33" fill="{colour}" font-family="{SANS}" font-size="12" text-anchor="middle">{language}</text>
{text}
</svg>
"""


def main():
    os.makedirs(FOLDER, exist_ok=True)
    for repo, title, language, description in PROJECTS:
        with open(os.path.join(FOLDER, repo + ".svg"), "w", encoding="utf-8", newline="\n") as f:
            f.write(card(title, language, description))
    print("wrote %d cards into cards/" % len(PROJECTS))


if __name__ == "__main__":
    main()

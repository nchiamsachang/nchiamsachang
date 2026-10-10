"""Draws rocket.svg, the contribution chart shown on the profile README.

The chart is a 30-day line in the style of a stock chart. A day with
contributions pushes the "price" up, a day without lets it sink slowly, and a
rocket rides the end of the line.

Run from the repository folder:

    py scripts/rocket.py            needs a GITHUB_TOKEN environment variable
    py scripts/rocket.py --sample   uses made-up numbers, for a local preview

Only the Python standard library is used.
"""
import json
import math
import os
import sys
import urllib.request

USER = "nchiamsachang"
TICKER = "$NATHAN"
DAYS = 30

START_PRICE = 20.0
GAIN_PER_CONTRIBUTION = 2.2   # added to the price for each contribution
DAILY_DECAY = 0.94            # a day off keeps 94% of the price
FLOOR = 4.0                   # the price never sinks below this

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "rocket.svg")

SAMPLE = [0, 1, 0, 2, 0, 0, 3, 1, 0, 2, 4, 0, 1, 3, 0, 2, 5, 3, 0, 4, 2, 6, 3, 0, 5, 7, 4, 6, 8, 9]

GREEN = "#3fb950"
RED = "#f85149"

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def fetch_contributions(user, token):
    """Contribution counts for the last DAYS days, oldest first."""
    body = json.dumps({"query": QUERY, "variables": {"login": user}}).encode("utf-8")
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={"Authorization": "bearer " + token, "User-Agent": user},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        reply = json.load(response)
    if "errors" in reply:
        raise RuntimeError("GitHub returned an error: " + json.dumps(reply["errors"]))

    weeks = reply["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    days = [day for week in weeks for day in week["contributionDays"]]
    days.sort(key=lambda day: day["date"])
    return [day["contributionCount"] for day in days[-DAYS:]]


def price_series(counts):
    """The price before the first day, then the price after each day."""
    price = START_PRICE
    prices = [price]
    for count in counts:
        if count > 0:
            price = price + count * GAIN_PER_CONTRIBUTION
        else:
            price = max(FLOOR, price * DAILY_DECAY)
        prices.append(price)
    return prices


def week_change_percent(prices):
    """Percent change from a week ago to today, rounded to a whole number."""
    week_ago = prices[max(0, len(prices) - 8)]
    return round((prices[-1] - week_ago) / week_ago * 100)


def draw(counts):
    """The whole chart as SVG text."""
    prices = price_series(counts)
    last = len(prices) - 1

    low, high = min(prices), max(prices)
    if high - low < 10:
        high = low + 10

    def x(i):
        return 46 + i * (480 / last)

    def y(price):
        return 222 - (price - low) / (high - low) * 125

    points = " L".join("%.1f,%.1f" % (x(i), y(p)) for i, p in enumerate(prices))
    end_x, end_y = x(last), y(prices[last])

    change = week_change_percent(prices)
    colour = GREEN if change >= 0 else RED
    sign = "+" if change >= 0 else ""

    # the rocket points along the last three days of the line
    back = max(0, last - 3)
    heading = round(math.degrees(math.atan2(end_y - y(prices[back]), end_x - x(back)))) + 90
    rocket_x = end_x + 26 * math.sin(math.radians(heading))
    rocket_y = end_y - 26 * math.cos(math.radians(heading))

    contributed_today = counts[-1] > 0
    flame = (
        '<path class="flame" stroke="#f0883e" d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09"/>'
        if contributed_today else ""
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 680 260" width="680" height="260" role="img" aria-labelledby="title desc">
<title id="title">Contribution chart for {USER}</title>
<desc id="desc">A line chart of the last {DAYS} days. Days with contributions raise the line and days without lower it slowly. The line is {sign}{change}% over the last week.</desc>
<style>
@keyframes flicker {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.45; }} }}
.flame {{ animation: flicker 0.3s infinite; }}
</style>
<rect width="680" height="260" rx="12" fill="#0d1117"/>
<g fill="#8b949e"><circle cx="560" cy="70" r="1"/><circle cx="610" cy="110" r="1.2"/><circle cx="500" cy="30" r="1"/><circle cx="430" cy="52" r="1.2"/><circle cx="655" cy="170" r="1"/><circle cx="350" cy="24" r="1"/></g>
<g transform="translate(606,22) scale(1.8)" fill="none" stroke="#e6edf3" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M20.985 12.486a9 9 0 1 1-9.473-9.472c.405-.022.617.46.402.803a6 6 0 0 0 8.268 8.268c.344-.215.825-.004.803.401"/></g>
<g stroke="#21262d" stroke-width="1"><line x1="40" y1="90" x2="590" y2="90"/><line x1="40" y1="140" x2="590" y2="140"/><line x1="40" y1="190" x2="590" y2="190"/><line x1="40" y1="232" x2="590" y2="232"/></g>
<text x="24" y="34" fill="#8b949e" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="13">{TICKER} · {DAYS} days</text>
<text x="24" y="64" font-family="-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"><tspan fill="#e6edf3" font-size="26" font-weight="600">{prices[last]:.1f}</tspan><tspan fill="{colour}" font-size="14" dx="10">{sign}{change}% this week</tspan></text>
<path d="M{points} L{end_x:.1f},232 L46,232 Z" fill="{colour}" fill-opacity="0.12"/>
<path d="M{points}" fill="none" stroke="{colour}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>
<circle cx="{end_x:.1f}" cy="{end_y:.1f}" r="4" fill="{colour}"/>
<g transform="translate({rocket_x:.1f},{rocket_y:.1f}) rotate({heading - 45})"><g transform="scale(1.5) translate(-12,-12)" fill="none" stroke="#e6edf3" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
{flame}
<path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/>
<path d="M9 12a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.4 22.4 0 0 1-4 2z"/>
<path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 .05 5 .05"/>
</g></g>
<text x="40" y="250" fill="#8b949e" font-family="-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif" font-size="11">{DAYS} days ago</text>
<text x="536" y="250" fill="#8b949e" font-family="-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif" font-size="11" text-anchor="end">today</text>
</svg>
"""


def main():
    if "--sample" in sys.argv:
        counts = SAMPLE
    else:
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            sys.exit("Set GITHUB_TOKEN, or run with --sample for a preview with made-up numbers.")
        counts = fetch_contributions(USER, token)

    with open(OUTPUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(draw(counts))
    print("Wrote rocket.svg from %d days, %d contributions in total." % (len(counts), sum(counts)))


if __name__ == "__main__":
    main()

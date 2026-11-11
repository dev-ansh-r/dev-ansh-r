"""Contribution graph styled as a Project Hail Mary mission log -> assets/mission.svg

Run:  python scripts/gen_mission.py
Token: GITHUB_TOKEN / GH_TOKEN env var, else `gh auth token`. Runs daily in CI.
"""
import json
import os
import random
import subprocess
import urllib.request
from datetime import date

from gen_assets import CARD, INK, LINE, MUTED, ORANGE, OUT, SOFT, TEXT, svg

USER = os.environ.get("PROFILE_USER", "dev-ansh-r")
QUERY = """query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{
totalContributions weeks{contributionDays{date contributionCount weekday}}}}}}"""

# Petrova-line glow: empty -> faint ember -> coral -> white-hot
LEVELS = ["#161616", "#3B2219", "#7A3D2A", "#B85E41", "#D97757", "#F6C3AA"]


def token():
    for k in ("GITHUB_TOKEN", "GH_TOKEN"):
        if os.environ.get(k):
            return os.environ[k]
    return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"u": USER}}).encode(),
        headers={"Authorization": f"bearer {token()}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        cal = json.load(r)["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return cal["totalContributions"], [w["contributionDays"] for w in cal["weeks"]]


def stats(weeks):
    days = [d for w in weeks for d in w]
    best = max(days, key=lambda d: d["contributionCount"])
    longest = cur = 0
    for d in days:
        cur = cur + 1 if d["contributionCount"] else 0
        longest = max(longest, cur)
    current = 0
    for d in reversed(days):
        if d["contributionCount"]:
            current += 1
        elif d is days[-1]:
            continue          # today may simply not have started yet
        else:
            break
    active = sum(1 for d in days if d["contributionCount"])
    return best, longest, current, active


def level(n, q):
    if n == 0:
        return 0
    for i, cut in enumerate(q, 1):
        if n <= cut:
            return i
    return 5


def main():
    total, weeks = fetch()
    best, longest, current, active = stats(weeks)
    counts = sorted(d["contributionCount"] for w in weeks for d in w if d["contributionCount"])
    q = [counts[int(len(counts) * f)] for f in (0.25, 0.5, 0.75, 0.93)] if counts else [1, 2, 3, 4]

    W, H = 1000, 380
    gx, gy, cell, pad = 64, 128, 13, 3.4
    rnd = random.Random(42)
    stars = "".join(
        f'<circle cx="{rnd.uniform(0, W):.0f}" cy="{rnd.uniform(0, H):.0f}" r="{rnd.choice([0.6, 0.8, 1, 1.3]):.1f}" '
        f'fill="#FFFFFF" opacity="{rnd.uniform(0.15, 0.7):.2f}"'
        + (f' class="tw" style="animation-delay:-{rnd.uniform(0, 4):.1f}s"' if rnd.random() < 0.25 else "")
        + "/>"
        for _ in range(140)
    )

    cells, months, last_m = [], [], None
    for wi, w in enumerate(weeks):
        x = gx + wi * (cell + pad)
        for d in w:
            y = gy + d["weekday"] * (cell + pad)
            lv = level(d["contributionCount"], q)
            glow = ' filter="url(#petrova)"' if lv >= 4 else ""
            cells.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell}" height="{cell}" rx="3" fill="{LEVELS[lv]}"{glow}>'
                         f'<title>{d["date"]}: {d["contributionCount"]}</title></rect>')
        m = date.fromisoformat(w[0]["date"]).strftime("%b").upper()
        if m != last_m and wi < len(weeks) - 2:
            months.append(f'<text x="{x:.1f}" y="{gy-10}" class="mono" font-size="9.5" fill="{MUTED}">{m}</text>')
            last_m = m
    gw = len(weeks) * (cell + pad)
    days_lbl = "".join(
        f'<text x="{gx-10}" y="{gy + i*(cell+pad) + 10}" text-anchor="end" class="mono" font-size="9" fill="{MUTED}">{l}</text>'
        for i, l in ((1, "MON"), (3, "WED"), (5, "FRI"))
    )

    # Sol -> Tau Ceti trajectory above the grid
    sx, tx, ty = gx + 6, gx + gw - 10, 86
    traj = f"M {sx} {ty} C {sx + gw*0.3} {ty-44}, {tx - gw*0.3} {ty-44}, {tx} {ty}"
    first, last = weeks[0][0]["date"], weeks[-1][-1]["date"]

    readouts = [
        ("CONTRIBUTIONS", f"{total:,}"), ("ACTIVE DAYS", f"{active}"),
        ("LONGEST BURN", f"{longest} d"), ("CURRENT BURN", f"{current} d"),
        ("PEAK OUTPUT", f'{best["contributionCount"]} · {date.fromisoformat(best["date"]).strftime("%d %b").upper()}'),
    ]
    rw = (W - 128) / len(readouts)
    ro = "".join(
        f'<text x="{64 + i*rw:.0f}" y="{H-58}" class="mono" font-size="9.5" fill="{MUTED}" letter-spacing="2">{k}</text>'
        f'<text x="{64 + i*rw:.0f}" y="{H-34}" class="mono" font-size="20" font-weight="700" fill="{TEXT}">{v}</text>'
        for i, (k, v) in enumerate(readouts)
    )

    body = f"""
<defs>
  <filter id="petrova" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="2.2" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <radialGradient id="tau" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#FFE3B0"/><stop offset="0.5" stop-color="{ORANGE}"/><stop offset="1" stop-color="{ORANGE}" stop-opacity="0"/></radialGradient>
  <radialGradient id="sol" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#FFFFFF"/><stop offset="0.45" stop-color="#FFE9A8"/><stop offset="1" stop-color="#FFE9A8" stop-opacity="0"/></radialGradient>
  <clipPath id="r"><rect width="{W}" height="{H}" rx="18"/></clipPath>
</defs>
<g clip-path="url(#r)">
  <rect width="{W}" height="{H}" fill="{INK}"/>
  {stars}
  <text x="40" y="40" class="mono" font-size="14" fill="{ORANGE}" letter-spacing="1">// mission log · hail mary</text>
  <text x="{W-40}" y="40" text-anchor="end" class="mono" font-size="11" fill="{MUTED}" letter-spacing="1.5">DESTINATION  TAU CETI  ·  11.9 LY</text>
  <path d="{traj}" fill="none" stroke="{LINE}" stroke-width="1.4" stroke-dasharray="3 6"/>
  <path d="{traj}" fill="none" stroke="{ORANGE}" stroke-width="2" stroke-dasharray="60 2000" class="burn"/>
  <circle cx="{sx}" cy="{ty}" r="14" fill="url(#sol)"/>
  <text x="{sx}" y="{ty-22}" text-anchor="middle" class="mono" font-size="9" fill="{SOFT}">SOL</text>
  <circle cx="{tx}" cy="{ty}" r="16" fill="url(#tau)" class="pulse"/>
  <text x="{tx}" y="{ty-24}" text-anchor="middle" class="mono" font-size="9" fill="{SOFT}">TAU CETI</text>
  <text x="{W/2}" y="{ty-48}" text-anchor="middle" class="mono" font-size="9" fill="{MUTED}" letter-spacing="2">{first}  →  {last}</text>
  {''.join(months)}
  {days_lbl}
  {''.join(cells)}
  <line x1="40" y1="{H-86}" x2="{W-40}" y2="{H-86}" stroke="{LINE}"/>
  {ro}
  <text x="{W-40}" y="{H-12}" text-anchor="end" class="mono" font-size="9" fill="{MUTED}">fist my bump</text>
</g>"""
    css = (
        ".tw{animation:tw 4s ease-in-out infinite}@keyframes tw{50%{opacity:.05}}"
        ".burn{animation:burn 9s linear infinite}@keyframes burn{from{stroke-dashoffset:60}to{stroke-dashoffset:-1000}}"
        ".pulse{transform-box:fill-box;transform-origin:center;animation:pl 3s ease-in-out infinite}"
        "@keyframes pl{50%{transform:scale(1.25)}}"
    )
    svg("mission.svg", W, H, body, css)
    print(f"mission.svg: {total} contributions")


if __name__ == "__main__":
    main()

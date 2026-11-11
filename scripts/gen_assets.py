"""Generate the profile README's SVG visuals into assets/.

Run:  python scripts/gen_assets.py
Every visual is plain SVG with system fonts and CSS animation, so it renders
inside GitHub's <img> sandbox (no external fonts, scripts or images).
"""
import re
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)

# palette: mono + coral
INK = "#0A0A0A"
CARD = "#141414"
LINE = "#262626"
TEXT = "#FAFAFA"
MUTED = "#8A8A8A"
SOFT = "#CFCFCF"
RED = "#D97757"
ORANGE = "#D97757"
GOLD = "#EDB49C"
GREEN = "#2F5D50"   # mantra green
CREAM = "#F6F2E8"

SANS = "'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif"
MONO = "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"
SERIF = "Georgia, 'Times New Roman', serif"


def t(s):
    return escape(s)


def svg(name, w, h, body, style=""):
    doc = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img">\n'
        f"<style>\n.sans{{font-family:{SANS}}} .mono{{font-family:{MONO}}} .serif{{font-family:{SERIF}}}\n"
        f"{style}\n</style>\n{body}\n</svg>\n"
    )
    (OUT / name).write_text(doc, encoding="utf-8")
    print("wrote", name)


def wind(y0, n, color, w=1000, op=0.35, dur=9):
    """Drifting wind strokes (Kaze)."""
    out = []
    for i in range(n):
        y = y0 + i * 14
        d = f"M -50 {y} C {w*0.25} {y-18}, {w*0.5} {y+18}, {w+50} {y-6}"
        out.append(
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{1.6 - i*0.25:.2f}" '
            f'stroke-linecap="round" stroke-dasharray="90 520" opacity="{op - i*0.07:.2f}" '
            f'class="wind" style="animation-duration:{dur + i*2}s;animation-delay:-{i*3}s"/>'
        )
    return "\n".join(out)


WIND_CSS = (
    ".wind{animation:drift linear infinite}"
    "@keyframes drift{from{stroke-dashoffset:610}to{stroke-dashoffset:0}}"
)


# ---------------------------------------------------------------- katana
_kid = [0]
KGOLD = "#D4A72C"
KGOLD_D = "#8C6A14"


def katana(x, y, length, angle=0, glint=True):
    """Gold-and-black katana: silk-wrapped tsuka with white same diamonds, black
    kashira/fuchi, round gold-rimmed tsuba, brass habaki, curved blade with bo-hi
    groove, cloudy hamon and kissaki. (x, y) = butt of the handle; blade along +x."""
    _kid[0] += 1
    k = _kid[0]
    L = length
    h = max(L * 0.03, 4.5)            # blade height at the guard
    hl = L * 0.27                     # handle length
    th = h * 1.4                      # handle height
    tg = h * 0.42                     # tsuba thickness
    b0 = hl + tg + h * 1.0            # blade start, after habaki
    sori = L * 0.032
    sw = lambda v: f"{max(L * v, 0.5):.2f}"  # stroke width scaled to length

    # tsuka: gold wrap with white diamonds
    cap = th * 0.55
    fuchi = th * 0.45
    wrap0, wrap1 = cap, hl - fuchi
    n = max(int((wrap1 - wrap0) / (th * 0.9)), 4)
    step = (wrap1 - wrap0) / n
    dia, cross = [], []
    for i in range(n):
        c = wrap0 + step * (i + 0.5)
        d = step * 0.36
        dia.append(f'<path d="M {c-d:.1f} 0 L {c:.1f} {-th*0.3:.1f} L {c+d:.1f} 0 L {c:.1f} {th*0.3:.1f} Z" fill="#EFEDE6"/>')
        cross.append(
            f'<path d="M {c-step/2:.1f} {-th/2:.1f} L {c+step/2:.1f} {th/2:.1f} '
            f'M {c-step/2:.1f} {th/2:.1f} L {c+step/2:.1f} {-th/2:.1f}" stroke="{KGOLD_D}" stroke-width="{sw(0.0025)}" opacity="0.8"/>'
        )
    handle = f"""
  <rect x="0" y="{-th/2:.1f}" width="{hl:.1f}" height="{th:.1f}" rx="{th*0.28:.1f}" fill="url(#silk{k})"/>
  {''.join(dia)}{''.join(cross)}
  <rect x="0" y="{-th*0.56:.1f}" width="{cap:.1f}" height="{th*1.12:.1f}" rx="{th*0.25:.1f}" fill="#111" stroke="{KGOLD}" stroke-width="{sw(0.003)}"/>
  <rect x="{hl-fuchi:.1f}" y="{-th*0.55:.1f}" width="{fuchi:.1f}" height="{th*1.1:.1f}" rx="{th*0.12:.1f}" fill="#111" stroke="{KGOLD}" stroke-width="{sw(0.002)}"/>"""

    # blade geometry
    tip_x = L
    tip_y = -sori - h * 0.1
    back = (f"M {b0:.1f} {-h/2:.1f} Q {(b0+L)/2:.1f} {-h/2-sori*1.15:.1f} {L-h*1.7:.1f} {-sori-h*0.6:.1f} "
            f"L {tip_x:.1f} {tip_y:.1f}")
    edge = f"Q {(b0+L)/2:.1f} {h/2-sori*0.95:.1f} {b0:.1f} {h/2:.1f} Z"
    blade = back + " " + edge
    edge_line = (f"M {tip_x:.1f} {tip_y:.1f} Q {(b0+L)/2:.1f} {h/2-sori*0.95:.1f} {b0:.1f} {h/2:.1f}")
    # cloudy hamon region (clipped to the blade)
    pts, segs = [], 22
    for i in range(segs + 1):
        f = i / segs
        px = b0 + (L - h * 1.9 - b0) * f
        mid = -sori * 4 * f * (1 - f) * 0.95 - sori * f * 0.85
        wob = (0.16 if i % 2 else 0.0) + (0.07 if i % 3 == 0 else 0)
        pts.append(f"{px:.1f} {mid + h*0.12 + h*wob:.1f}")
    hamon_line = "M " + " L ".join(pts)
    hamon = f"M {b0:.1f} {h:.1f} L " + " L ".join(pts) + f" L {L:.1f} {tip_y:.1f} L {L:.1f} {h*2:.1f} L {b0:.1f} {h*2:.1f} Z"
    bohi = (f"M {b0+h*1.4:.1f} {-h*0.22:.1f} Q {(b0+L)/2:.1f} {-h*0.22-sori*1.1:.1f} "
            f"{L*0.82:.1f} {-sori*0.95-h*0.38:.1f}")
    yokote = f"M {L-h*1.7:.1f} {-sori-h*0.6:.1f} L {L-h*1.95:.1f} {-sori+h*0.05:.1f}"
    glint_svg = (
        f'<path d="{bohi}" fill="none" stroke="#FFFFFF" stroke-width="{max(L*0.006,1.4):.2f}" '
        f'stroke-linecap="round" stroke-dasharray="{L*0.08:.0f} {L*2:.0f}" class="glint"/>'
        if glint else ""
    )
    hx = hl + tg
    return f"""
<g transform="translate({x} {y}) rotate({angle})">
  <defs>
    <linearGradient id="steel{k}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#7E848A"/><stop offset="0.4" stop-color="#B9BFC5"/><stop offset="0.75" stop-color="#9DA3A9"/><stop offset="1" stop-color="#C8CED4"/></linearGradient>
    <linearGradient id="silk{k}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#F0C94B"/><stop offset="0.5" stop-color="{KGOLD}"/><stop offset="1" stop-color="{KGOLD_D}"/></linearGradient>
    <linearGradient id="brass{k}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#F3DC8A"/><stop offset="1" stop-color="#9C7A22"/></linearGradient>
    <clipPath id="bl{k}"><path d="{blade}"/></clipPath>
  </defs>
  {handle}
  <path d="{blade}" fill="url(#steel{k})"/>
  <g clip-path="url(#bl{k})">
    <path d="{hamon}" fill="#F4F7FA" opacity="0.78"/>
    <path d="{hamon_line}" fill="none" stroke="#5F656B" stroke-width="{max(h*0.05,0.5):.2f}" opacity="0.55"/>
    <path d="{bohi}" fill="none" stroke="#6E747A" stroke-width="{max(h*0.13,0.8):.2f}" stroke-linecap="round"/>
    <path d="{bohi}" fill="none" stroke="#FFFFFF" stroke-width="{max(h*0.04,0.4):.2f}" opacity="0.7" transform="translate(0 {h*0.09:.2f})"/>
  </g>
  <path d="{edge_line}" fill="none" stroke="#D6ECFF" stroke-width="{sw(0.0022)}" opacity="0.8"/>
  <path d="{yokote}" stroke="#7C8288" stroke-width="{sw(0.002)}"/>
  {glint_svg}
  <rect x="{hx:.1f}" y="{-h*0.66:.1f}" width="{h*1.0:.1f}" height="{h*1.32:.1f}" rx="{h*0.12:.1f}" fill="url(#brass{k})"/>
  <ellipse cx="{hl+tg/2:.1f}" cy="0" rx="{tg/2+h*0.08:.1f}" ry="{th*1.1:.1f}" fill="#141414" stroke="{KGOLD}" stroke-width="{sw(0.004)}"/>
  <ellipse cx="{hl+tg/2:.1f}" cy="0" rx="{tg*0.18:.1f}" ry="{th*0.75:.1f}" fill="none" stroke="{KGOLD}" stroke-width="{sw(0.002)}" opacity="0.8"/>
</g>"""


KATANA_CSS = (
    ".glint{animation:glint 5s ease-in-out infinite}"
    "@keyframes glint{0%,55%{stroke-dashoffset:0;opacity:0}60%{opacity:.9}100%{stroke-dashoffset:-900;opacity:0}}"
)


# ---------------------------------------------------------------- katana (photo)
# Photo: "Blades and Mountings for a Pair of Swords (Daisho)", The Metropolitan
# Museum of Art, CC0 via Wikimedia Commons. Top sword cropped, flipped, background removed.
KATANA_RATIO = 153 / 1566
_pk = [0]


def photo_katana(x, y, width, angle=0, rim="#FFFFFF", rim_op=0.35):
    """Embed the real katana photo; (x, y) = handle end, centred vertically."""
    import base64
    _pk[0] += 1
    k = _pk[0]
    data = base64.b64encode((OUT / "katana.webp").read_bytes()).decode()
    h = width * KATANA_RATIO
    return (
        f'<defs><filter id="rim{k}" x="-5%" y="-40%" width="110%" height="180%">'
        f'<feDropShadow dx="0" dy="0" stdDeviation="{max(width/260,1.2):.1f}" flood-color="{rim}" flood-opacity="{rim_op}"/>'
        f'</filter></defs>'
        f'<g transform="translate({x} {y}) rotate({angle})">'
        f'<image x="0" y="{-h/2:.1f}" width="{width}" height="{h:.1f}" filter="url(#rim{k})" '
        f'href="data:image/webp;base64,{data}"/></g>'
    )


# ---------------------------------------------------------------- hero
def hero():
    W, H = 1000, 340
    px0, py0, px1, py1 = 560, 26, 974, 314   # engineering drawing panel
    grid = []
    for gx in range(px0, px1 + 1, 12):
        c = "#1F1F1F" if (gx - px0) % 60 == 0 else "#151515"
        grid.append(f'<line x1="{gx}" y1="{py0}" x2="{gx}" y2="{py1}" stroke="{c}"/>')
    for gy in range(py0, py1 + 1, 12):
        c = "#1F1F1F" if (gy - py0) % 60 == 0 else "#151515"
        grid.append(f'<line x1="{px0}" y1="{gy}" x2="{px1}" y2="{gy}" stroke="{c}"/>')
    marks = "".join(
        f'<path d="M {x-8} {y} H {x+8} M {x} {y-8} V {y+8}" stroke="{MUTED}" stroke-width="1"/>'
        f'<circle cx="{x}" cy="{y}" r="4" fill="none" stroke="{MUTED}" stroke-width="1"/>'
        for x, y in [(px0 + 14, py0 + 14), (px1 - 14, py0 + 14), (px0 + 14, py1 - 14)]
    )
    # portrait (U1 = the human) + spec sheet about me
    import base64
    photo = base64.b64encode((OUT / "avatar.jpg").read_bytes()).decode()
    pcx, pcy, pr = 650, 140, 58
    ring = (
        f'<circle cx="{pcx}" cy="{pcy}" r="{pr+10}" fill="none" stroke="{ORANGE}" stroke-width="1" stroke-dasharray="2 5" class="spin"/>'
        f'<circle cx="{pcx}" cy="{pcy}" r="{pr+2}" fill="none" stroke="{ORANGE}" stroke-width="2"/>'
        f'<path d="M {pcx-pr-22} {pcy} H {pcx-pr-6} M {pcx+pr+6} {pcy} H {pcx+pr+22} '
        f'M {pcx} {pcy-pr-22} V {pcy-pr-6} M {pcx} {pcy+pr+6} V {pcy+pr+22}" stroke="{ORANGE}" stroke-width="1.4"/>'
        f'<image x="{pcx-pr}" y="{pcy-pr}" width="{pr*2}" height="{pr*2}" clip-path="url(#face)" '
        f'href="data:image/jpeg;base64,{photo}"/>'
        f'<text x="{pcx}" y="{pcy+pr+44}" text-anchor="middle" class="mono" font-size="10" fill="{TEXT}" letter-spacing="2">U1 · HUMAN</text>'
        f'<text x="{pcx}" y="{pcy+pr+58}" text-anchor="middle" class="mono" font-size="8.5" fill="{MUTED}">the one doing the building</text>'
    )
    rows = [
        ("BASE", "Coimbatore, India"),
        ("FOCUS", "Physical AI · Robotics"),
        ("ROLE", "Engineer · Entrepreneur"),
        ("COMMUNITY", "AI Tamil Nadu"),
        ("RIDES", "Kaze · Himalayan 450"),
        ("FUEL", "Anime, Games (Jin Sakai)"),
        ("MODE", "build · break · rebuild"),
    ]
    rx, ry0, step = 742, 66, 29
    spec = [f'<text x="{rx}" y="{ry0-22}" class="mono" font-size="9" fill="{ORANGE}" letter-spacing="2">SPEC SHEET</text>',
            f'<path d="M {rx} {ry0-14} H {px1-20}" stroke="#2A2A2A"/>']
    for i, (k_, v) in enumerate(rows):
        y = ry0 + i * step
        spec.append(
            f'<text x="{rx}" y="{y}" class="mono" font-size="8.5" fill="{MUTED}" letter-spacing="1.5">{k_}</text>'
            f'<text x="{rx+72}" y="{y}" class="sans" font-size="12" fill="{TEXT}">{t(v)}</text>'
            f'<path d="M {rx} {y+10} H {px1-20}" stroke="#1C1C1C"/>'
        )
    tb = (
        f'<rect x="{px1-186}" y="{py1-34}" width="186" height="34" fill="{INK}" stroke="#2A2A2A"/>'
        f'<path d="M {px1-186} {py1-17} H {px1} M {px1-96} {py1-34} V {py1}" stroke="#2A2A2A"/>'
        f'<text x="{px1-180}" y="{py1-22}" class="mono" font-size="8" fill="{MUTED}">DWG  DS-001</text>'
        f'<text x="{px1-90}" y="{py1-22}" class="mono" font-size="8" fill="{MUTED}">REV  2026</text>'
        f'<text x="{px1-180}" y="{py1-5}" class="mono" font-size="8" fill="{MUTED}">BUILT IN</text>'
        f'<text x="{px1-90}" y="{py1-5}" class="mono" font-size="8" fill="{ORANGE}">COIMBATORE</text>'
    )
    body = f"""
<defs>
  <radialGradient id="glow" cx="0.66" cy="0.42" r="0.32"><stop offset="0" stop-color="{ORANGE}" stop-opacity="0.18"/><stop offset="1" stop-color="{ORANGE}" stop-opacity="0"/></radialGradient>
  <clipPath id="face"><circle cx="{pcx}" cy="{pcy}" r="{pr}"/></clipPath>
  <clipPath id="r"><rect width="{W}" height="{H}" rx="18"/></clipPath>
</defs>
<g clip-path="url(#r)">
  <rect width="{W}" height="{H}" fill="{INK}"/>
  <g>{''.join(grid)}</g>
  <rect x="{px0}" y="{py0}" width="{px1-px0}" height="{py1-py0}" fill="none" stroke="#2A2A2A"/>
  <rect width="{W}" height="{H}" fill="url(#glow)"/>
  {marks}
  {ring}
  {''.join(spec)}
  {tb}
  <text x="56" y="84" class="mono" font-size="15" fill="{ORANGE}" letter-spacing="1">// physical ai &amp; robotics</text>
  <text x="54" y="152" class="sans" font-size="76" font-weight="800" fill="{TEXT}" letter-spacing="-1.5">Devansh</text>
  {photo_katana(56, 186, 440, -1)}
  <text x="56" y="242" class="sans" font-size="19" fill="{SOFT}">Engineer  ·  Entrepreneur  ·  Community Lead  ·  Open Source</text>
  <text x="56" y="276" class="sans" font-size="16" fill="{MUTED}">I build intelligent machines, ones that run on metal.</text>
</g>"""
    css = (
        KATANA_CSS
        + ".spin{transform-box:fill-box;transform-origin:center;animation:spin 30s linear infinite}"
        + "@keyframes spin{to{transform:rotate(360deg)}}"
    )
    svg("hero.svg", W, H, body, css)


# ---------------------------------------------------------------- mantra
def mantra():
    W, H = 1000, 230
    cx, cy = 500, 58
    petals = "".join(
        f'<ellipse cx="{cx}" cy="{cy-15}" rx="5.5" ry="15" transform="rotate({a} {cx} {cy})"/>'
        for a in range(0, 360, 30)
    )
    inner = "".join(
        f'<ellipse cx="{cx}" cy="{cy-8}" rx="3" ry="8" transform="rotate({a+15} {cx} {cy})"/>'
        for a in range(0, 360, 30)
    )
    body = f"""
<rect width="{W}" height="{H}" rx="18" fill="{CREAM}"/>
<rect x="10" y="10" width="{W-20}" height="{H-20}" rx="12" fill="none" stroke="#E4DCC8" stroke-width="1"/>
<g class="mandala" fill="none" stroke="{GREEN}" stroke-width="1.4">{petals}</g>
<g class="mandala rev" fill="none" stroke="#7FA392" stroke-width="1.2">{inner}</g>
<circle cx="{cx}" cy="{cy}" r="3" fill="{GREEN}"/>
<text x="{cx}" y="138" text-anchor="middle" class="sans" font-size="38" font-weight="700" fill="{GREEN}">lokāḥ samastāḥ sukhino bhavantu</text>
<text x="{cx}" y="172" text-anchor="middle" class="serif" font-size="18" font-style="italic" fill="#5E8172">may all beings everywhere be happy and free</text>
<text x="{cx}" y="205" text-anchor="middle" class="mono" font-size="11" fill="#9DB3A8" letter-spacing="4">WHY I BUILD</text>"""
    css = (
        ".mandala{transform-box:fill-box;transform-origin:center;animation:spin 60s linear infinite}"
        ".rev{animation-direction:reverse;animation-duration:40s}"
        "@keyframes spin{to{transform:rotate(360deg)}}"
    )
    svg("mantra.svg", W, H, body, css)


# ---------------------------------------------------------------- loop
def loop():
    W, H = 1000, 250
    steps = [("01", "Build things.", ORANGE), ("02", "Break things.", RED),
             ("03", "Understand why.", GOLD), ("04", "Build again.", ORANGE)]
    xs = [125, 375, 625, 875]
    y = 112
    nodes = []
    for i, ((n, label, c), x) in enumerate(zip(steps, xs)):
        nodes.append(
            f'<circle cx="{x}" cy="{y}" r="36" fill="{CARD}" stroke="{LINE}" stroke-width="2"/>'
            f'<circle cx="{x}" cy="{y}" r="36" fill="none" stroke="{c}" stroke-width="3" class="lit" style="animation-delay:{i*1.5}s"/>'
            f'<text x="{x}" y="{y+8}" text-anchor="middle" class="mono" font-size="22" font-weight="700" fill="{c}">{n}</text>'
            f'<text x="{x}" y="{y+70}" text-anchor="middle" class="sans" font-size="19" font-weight="700" fill="{TEXT}">{t(label)}</text>'
        )
    arrows = "".join(
        f'<path d="M {xs[i]+46} {y} H {xs[i+1]-46}" stroke="{LINE}" stroke-width="2" marker-end="url(#ah)"/>'
        for i in range(3)
    )
    loop_d = f"M {xs[0]} {y} H {xs[3]} M {xs[3]} {y+36} C {xs[3]} {H-6}, {xs[0]} {H-6}, {xs[0]} {y+36}"
    ret = f"M {xs[3]} {y+92} C {xs[3]-40} {H-8}, {xs[0]+40} {H-8}, {xs[0]} {y+92}"
    body = f"""
<defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10z" fill="{LINE}"/></marker></defs>
<rect width="{W}" height="{H}" rx="18" fill="{INK}"/>
<text x="40" y="44" class="mono" font-size="14" fill="{ORANGE}" letter-spacing="1">// how i work</text>
{arrows}
<path d="{ret}" fill="none" stroke="{LINE}" stroke-width="2" stroke-dasharray="4 7"/>
<path d="{ret}" fill="none" stroke="{ORANGE}" stroke-width="2.5" stroke-dasharray="40 900" class="back"/>
{''.join(nodes)}"""
    css = (
        ".lit{opacity:0;animation:lit 6s ease-in-out infinite}"
        "@keyframes lit{0%,30%{opacity:0}8%,20%{opacity:1}}"
        ".back{animation:back 6s linear infinite}@keyframes back{from{stroke-dashoffset:940}to{stroke-dashoffset:0}}"
    )
    svg("loop.svg", W, H, body, css)


# ---------------------------------------------------------------- project cards
def pill_row(x, y, tags, color, size=12, gap=8):
    out, cx = [], x
    for tag in tags:
        w = len(tag) * size * 0.62 + 20
        out.append(
            f'<rect x="{cx}" y="{y}" width="{w:.0f}" height="24" rx="12" fill="none" stroke="{color}" stroke-opacity="0.55"/>'
            f'<text x="{cx + w/2:.0f}" y="{y+16}" text-anchor="middle" class="mono" font-size="{size}" fill="{SOFT}">{t(tag)}</text>'
        )
        cx += w + gap
    return "".join(out)


def card(name, kicker, title, lines, tags, color, logo=None):
    W, H = 490, 206
    desc = "".join(
        f'<text x="34" y="{(124 if logo else 118) + i*22}" class="sans" font-size="15" fill="{MUTED}">{t(l)}</text>'
        for i, l in enumerate(lines)
    )
    if logo:
        import base64
        data = base64.b64encode((OUT / logo[0]).read_bytes()).decode()
        lh = 58
        title_svg = (f'<image x="30" y="50" height="{lh}" width="{lh * logo[1]:.0f}" '
                     f'href="data:image/png;base64,{data}"/>')
    else:
        title_svg = f'<text x="34" y="80" class="sans" font-size="25" font-weight="800" fill="{TEXT}">{t(title)}</text>'
    body = f"""
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="16" fill="{CARD}" stroke="{LINE}" stroke-width="1.5"/>
<rect x="1" y="24" width="5" height="{H-48}" rx="2.5" fill="{color}"/>
<text x="34" y="40" class="mono" font-size="11.5" fill="{color}" letter-spacing="2">{t(kicker)}</text>
{title_svg}
<text x="{W-34}" y="80" text-anchor="end" class="mono" font-size="18" fill="{color}">↗</text>
{desc}
{pill_row(34, 162, tags, color)}"""
    svg(name, W, H, body)


def cards():
    card("card-qroot.svg", "PHYSICAL AI · ROBOTICS", "Qroot microbot",
         ["A walking microbot that senses, thinks and moves", "on a single edge board. No PC. No cloud."],
         ["Robotics", "C++", "Python", "RealSense"], "#22C55E", logo=("qroot-logo.png", 480 / 205))
    card("card-skills.svg", "CLAUDE CODE · EDGE AI", "qualcomm-claude-skills",
         ["8 Claude Code skills that turn hard-won edge", "deployment know-how into repeatable flows."],
         ["Claude Code", "Edge AI", "Quantization", "Apache-2.0"], RED)
    card("card-rocky.svg", "DESKTOP · MODEL INTROSPECTION", "Rocky",
         ["Understand any neural network architecture,", "paper-grounded. Short sentences. Fist bump."],
         ["Rust", "TypeScript", "Python", "MCP"], GOLD)
    card("card-supertonic.svg", "TEXT-TO-SPEECH · LOW POWER AI", "Supertonic 2 · Edge",
         ["Latent-diffusion text-to-speech, quantized", "to run on low-power NPUs."],
         ["TTS", "W8A16", "ONNX", "Hugging Face"], ORANGE)


# ---------------------------------------------------------------- stack
ICONS = Path(__file__).resolve().parent / "icons"   # Simple Icons (CC0), 24x24 paths


def icon(slug, x, y, size, fill):
    """Inline a Simple Icons logo at (x, y), size px square."""
    d = re.search(r' d="([^"]+)"', (ICONS / f"{slug}.svg").read_text(encoding="utf-8")).group(1)
    return f'<path transform="translate({x} {y}) scale({size/24:.4f})" fill="{fill}" d="{d}"/>'


def stack():
    cols = [
        ("EDGE AI", [("NPU deployment", None), ("Quantization · PTQ/QAT", None), ("Jetson · TensorRT", "nvidia"),
                     ("Qualcomm QNN", "qualcomm"), ("ONNX", "onnx"), ("PyTorch", "pytorch"), ("OpenCV", "opencv")]),
        ("ROBOTICS", [("ROS 2", "ros"), ("Nav2", "ros"), ("SLAM / VIO", None), ("VLA models", "huggingface"),
                      ("Gazebo", None), ("RealSense", "intel"), ("micro-ROS", "ros")]),
        ("AI AGENTS", [("Claude Code", "claude"), ("Claude Agent SDK", "claude"), ("Claude API", "anthropic"),
                       ("MCP", None), ("LangGraph", "langchain"), ("Voice agents", None)]),
        ("EMBEDDED", [("C / C++", "cplusplus"), ("Python", "python"), ("Rust", "rust"), ("Yocto · Linux", "linux"),
                      ("Raspberry Pi", "raspberrypi"), ("Arduino · ESP32", "arduino"), ("LoRaWAN · MQTT", None)]),
    ]
    W, H = 1000, 370
    out = [f'<rect width="{W}" height="{H}" rx="18" fill="{INK}"/>',
           f'<text x="40" y="44" class="mono" font-size="14" fill="{ORANGE}" letter-spacing="1">// stack</text>']
    colw = (W - 80) / 4
    for i, (head, items) in enumerate(cols):
        x = 40 + i * colw
        out.append(f'<text x="{x}" y="88" class="mono" font-size="12" font-weight="700" fill="{ORANGE}" letter-spacing="3">{head}</text>')
        out.append(f'<rect x="{x}" y="98" width="28" height="3" rx="1.5" fill="{ORANGE}"/>')
        for j, (it, slug) in enumerate(items):
            y = 116 + j * 34
            w = len(it) * 8.0 + 40
            out.append(f'<rect x="{x}" y="{y}" width="{w:.0f}" height="28" rx="7" fill="{CARD}" stroke="{LINE}"/>')
            if slug:
                out.append(icon(slug, x + 8, y + 6, 16, TEXT))
            else:
                out.append(f'<circle cx="{x+16}" cy="{y+14}" r="3.5" fill="{ORANGE}"/>')
            out.append(f'<text x="{x+32}" y="{y+19}" class="sans" font-size="14" fill="{SOFT}">{t(it)}</text>')
    svg("stack.svg", W, H, "\n".join(out))


# ---------------------------------------------------------------- certs
def cert(name, color, title, sub, foot, glyph):
    W, H = 490, 120
    body = f"""
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="16" fill="{CARD}" stroke="{LINE}" stroke-width="1.5"/>
<circle cx="66" cy="60" r="34" fill="{color}" fill-opacity="0.14" stroke="{color}" stroke-width="2"/>
{glyph}
<text x="122" y="50" class="sans" font-size="21" font-weight="800" fill="{TEXT}">{t(title)}</text>
<text x="122" y="74" class="sans" font-size="14" fill="{MUTED}">{t(sub)}</text>
<text x="122" y="98" class="mono" font-size="11.5" fill="{color}" letter-spacing="1">{t(foot)}</text>"""
    svg(name, W, H, body)


def certs():
    cert("cert-claude.svg", "#D97757", "Claude Certified Architect",
         "Foundations · Anthropic", "VERIFY ON CREDLY ↗", icon("claude", 46, 40, 40, "#D97757"))
    cert("cert-nvidia.svg", "#76B900", "Accelerated Computing · CUDA",
         "Fundamentals with CUDA C/C++ · NVIDIA DLI", "VIEW CERTIFICATE ↗", icon("nvidia", 46, 40, 40, "#76B900"))


# ---------------------------------------------------------------- straw hat
def straw_hat(cx, cy, k=1.0):
    """An original straw-hat drawing: woven straw brim and crown, red band."""
    bw, bh = 92 * k, 15 * k          # brim half-width / half-height
    cw, ch = 44 * k, 36 * k          # crown half-width / height
    weave = "".join(
        f'<path d="M {cx-bw+10*k + i*14*k:.1f} {cy+2*k:.1f} q {7*k:.1f} {4*k:.1f} {14*k:.1f} 0" '
        f'fill="none" stroke="#B8902F" stroke-width="{1*k:.1f}" opacity="0.6"/>'
        for i in range(int((2 * bw - 20 * k) / (14 * k)))
    )
    crown_weave = "".join(
        f'<path d="M {cx-cw+6*k:.1f} {cy-6*k - j*7*k:.1f} Q {cx:.1f} {cy-10*k - j*7*k:.1f} {cx+cw-6*k:.1f} {cy-6*k - j*7*k:.1f}" '
        f'fill="none" stroke="#B8902F" stroke-width="{0.9*k:.1f}" opacity="0.5"/>'
        for j in range(2, 5)
    )
    return f"""
<g>
  <ellipse cx="{cx}" cy="{cy+6*k:.1f}" rx="{bw*1.02:.1f}" ry="{bh*0.9:.1f}" fill="#000" opacity="0.35"/>
  <ellipse cx="{cx}" cy="{cy}" rx="{bw:.1f}" ry="{bh:.1f}" fill="#E9C46A" stroke="#B8902F" stroke-width="{1.5*k:.1f}"/>
  {weave}
  <path d="M {cx-cw:.1f} {cy:.1f} C {cx-cw:.1f} {cy-ch*1.25:.1f}, {cx+cw:.1f} {cy-ch*1.25:.1f}, {cx+cw:.1f} {cy:.1f} Z" fill="#F0CF78" stroke="#B8902F" stroke-width="{1.5*k:.1f}"/>
  <path d="M {cx-cw:.1f} {cy-1*k:.1f} Q {cx:.1f} {cy+5*k:.1f} {cx+cw:.1f} {cy-1*k:.1f} L {cx+cw-2*k:.1f} {cy-11*k:.1f} Q {cx:.1f} {cy-6*k:.1f} {cx-cw+2*k:.1f} {cy-11*k:.1f} Z" fill="#C8102E"/>
</g>"""


# ---------------------------------------------------------------- off the clock
# ---------------------------------------------------------------- crew flag
def crew_flag(mx, my, k=1.0):
    """Original pirate flag: black flag waving off a wooden mast, plain skull and
    crossbones, and a straw hat hung on the mast top. (mx, my) = mast top."""
    s = lambda v: f"{v*k:.1f}"
    fx = mx - 3 * k   # flag attaches to the mast's left side
    flag = (f"M {fx:.1f} {my+14*k:.1f} "
            f"C {fx-38*k:.1f} {my+2*k:.1f}, {fx-72*k:.1f} {my+26*k:.1f}, {fx-112*k:.1f} {my+12*k:.1f} "
            f"C {fx-128*k:.1f} {my+8*k:.1f}, {fx-140*k:.1f} {my+14*k:.1f}, {fx-150*k:.1f} {my+12*k:.1f} "
            f"L {fx-144*k:.1f} {my+92*k:.1f} "
            f"C {fx-128*k:.1f} {my+96*k:.1f}, {fx-108*k:.1f} {my+86*k:.1f}, {fx-84*k:.1f} {my+96*k:.1f} "
            f"C {fx-52*k:.1f} {my+108*k:.1f}, {fx-26*k:.1f} {my+86*k:.1f}, {fx:.1f} {my+96*k:.1f} Z")
    cx, cy = fx - 74 * k, my + 52 * k          # emblem centre
    bone = "#F2EFE6"

    def crossbone(angle):
        L = 46 * k
        return (f'<g transform="rotate({angle} {cx:.1f} {cy+6*k:.1f})">'
                f'<rect x="{cx-L:.1f}" y="{cy+3*k:.1f}" width="{2*L:.1f}" height="{s(6)}" rx="{s(3)}" fill="{bone}"/>'
                + "".join(f'<circle cx="{cx+e*L:.1f}" cy="{cy+3*k+dy*k:.1f}" r="{s(4.2)}" fill="{bone}"/>'
                          for e in (-1, 1) for dy in (0, 6))
                + "</g>")
    skull = (
        f'<circle cx="{cx:.1f}" cy="{cy-4*k:.1f}" r="{s(17)}" fill="{bone}"/>'
        f'<rect x="{cx-10*k:.1f}" y="{cy+6*k:.1f}" width="{s(20)}" height="{s(12)}" rx="{s(3)}" fill="{bone}"/>'
        f'<ellipse cx="{cx-6.5*k:.1f}" cy="{cy-5*k:.1f}" rx="{s(4.6)}" ry="{s(5.4)}" fill="#0E0E0E"/>'
        f'<ellipse cx="{cx+6.5*k:.1f}" cy="{cy-5*k:.1f}" rx="{s(4.6)}" ry="{s(5.4)}" fill="#0E0E0E"/>'
        f'<path d="M {cx:.1f} {cy+1*k:.1f} l {s(-2.6)} {s(4.5)} h {s(5.2)} z" fill="#0E0E0E"/>'
        + "".join(f'<line x1="{cx+dx*k:.1f}" y1="{cy+10*k:.1f}" x2="{cx+dx*k:.1f}" y2="{cy+18*k:.1f}" stroke="#0E0E0E" stroke-width="{s(1.1)}"/>'
                  for dx in (-5, 0, 5))
    )
    mast = (
        f'<defs><linearGradient id="wood" x1="0" x2="1"><stop offset="0" stop-color="#6B4423"/>'
        f'<stop offset="0.5" stop-color="#A0703F"/><stop offset="1" stop-color="#5A381C"/></linearGradient></defs>'
        f'<rect x="{mx-3*k:.1f}" y="{my:.1f}" width="{s(7)}" height="{s(132)}" rx="{s(2)}" fill="url(#wood)"/>'
        f'<circle cx="{mx+0.5*k:.1f}" cy="{my-1*k:.1f}" r="{s(5)}" fill="#C9A15A"/>'
    )
    return f"""
<g>
  {mast}
  <g class="wave" style="transform-origin:{fx:.1f}px {my+50*k:.1f}px">
    <path d="{flag}" fill="#141414" stroke="#4A4A4A" stroke-width="{s(1.6)}"/>
    {crossbone(28)}{crossbone(-28)}
    {skull}
  </g>
  <g transform="rotate(-14 {mx:.1f} {my:.1f})">{straw_hat(mx + 2*k, my + 4*k, 0.36 * k)}</g>
</g>"""


FLAG_CSS = ".wave{animation:wave 4s ease-in-out infinite}@keyframes wave{50%{transform:skewY(-2.5deg) scaleX(.97)}}"


def _wrap(text, n=26):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        if cur and len(cur) + len(w_) + 1 > n:
            lines.append(cur); cur = w_
        else:
            cur = (cur + " " + w_).strip()
    lines.append(cur)
    return lines


def offclock():
    import base64
    W, H = 1000, 420
    tiles = [
        ("PLAYING", RED, ["Ghost of", "Tsushima"], "all-time favourite"),
        ("WATCHING", ORANGE, ["Movies", "Anime", "Manga"], "Shinobi of the Hidden Leaf"),
        ("CREW", GOLD, ["Straw Hat", "Pirates"], "captain's orders are captain's orders"),
        ("RIDING", ORANGE, ["Kaze  風"], "Himalayan 450 · named for the wind"),
    ]
    tw, gap, x0, y0, th = 215, 20, 40, 66, 172
    bike = base64.b64encode((OUT / "kaze.webp").read_bytes()).decode()
    out = [
        f'<rect width="{W}" height="{H}" rx="18" fill="{INK}"/>',
        wind(H - 40, 3, RED, W, 0.25, 11),
        f'<text x="40" y="44" class="mono" font-size="14" fill="{ORANGE}" letter-spacing="1">// off the clock</text>',
        f'<defs><linearGradient id="shadeL" x1="0" x2="1"><stop offset="0" stop-color="#000" stop-opacity="0.82"/>'
        f'<stop offset="0.55" stop-color="#000" stop-opacity="0.25"/><stop offset="1" stop-color="#000" stop-opacity="0"/></linearGradient>'
        f'<linearGradient id="shadeB" x1="0" y1="0" x2="0" y2="1"><stop offset="0.55" stop-color="#000" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="#000" stop-opacity="0.85"/></linearGradient></defs>',
    ]
    for i, (lab, c, big, sub) in enumerate(tiles):
        x = x0 + i * (tw + gap)
        out.append(f'<clipPath id="tile{i}"><rect x="{x}" y="{y0}" width="{tw}" height="{th}" rx="14"/></clipPath>')
        out.append(f'<rect x="{x}" y="{y0}" width="{tw}" height="{th}" rx="14" fill="{CARD}"/>')
        if lab == "CREW":     # original Grand Line scene: sky, clouds, sea
            sea_y = y0 + th * 0.70
            clouds = "".join(
                f'<ellipse cx="{x+cx_:.0f}" cy="{y0+cy_:.0f}" rx="{rx_}" ry="{ry_}" fill="#FFFFFF" opacity="0.85"/>'
                for cx_, cy_, rx_, ry_ in [(150, 92, 26, 9), (168, 86, 18, 9), (178, 112, 16, 5)]
            )
            waves = "".join(
                f'<path d="M {x} {sea_y + 8 + j*12:.0f} ' + " ".join(f"q 9 -5 18 0" for _ in range(13)) + f'" fill="none" stroke="#9FD3FF" stroke-width="1.2" opacity="{0.6 - j*0.2:.1f}"/>'
                for j in range(3)
            )
            out.append(
                f'<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1F5FB8"/>'
                f'<stop offset="1" stop-color="#7DB8F0"/></linearGradient></defs>'
                f'<g clip-path="url(#tile{i})"><rect x="{x}" y="{y0}" width="{tw}" height="{th}" fill="url(#sky)"/>{clouds}'
                f'<rect x="{x}" y="{sea_y:.0f}" width="{tw}" height="{th}" fill="#123A6B"/>{waves}'
                f'<rect x="{x}" y="{y0}" width="{tw}" height="{th}" fill="url(#shadeL)" opacity="0.75"/>'
                f'<rect x="{x}" y="{y0}" width="{tw}" height="{th}" fill="url(#shadeB)" opacity="0.6"/></g>'
            )
        if lab == "RIDING":   # Kaze: full-bleed photo, shaded for text
            out.append(
                f'<g clip-path="url(#tile{i})">'
                f'<image x="{x}" y="{y0}" width="{tw}" height="{th}" preserveAspectRatio="xMidYMid slice" '
                f'href="data:image/webp;base64,{bike}"/>'
                f'<rect x="{x}" y="{y0}" width="{tw}" height="{th}" fill="url(#shadeL)"/>'
                f'<rect x="{x}" y="{y0}" width="{tw}" height="{th}" fill="url(#shadeB)"/></g>'
            )
        out.append(f'<rect x="{x}" y="{y0}" width="{tw}" height="{th}" rx="14" fill="none" stroke="{LINE}" stroke-width="1.5"/>')
        out.append(f'<text x="{x+20}" y="{y0+30}" class="mono" font-size="11" fill="{c}" letter-spacing="3">{lab}</text>')
        size = 26 if len(big) < 3 else 21
        for j, b in enumerate(big):
            out.append(f'<text x="{x+20}" y="{y0+68 + j*(size+8)}" class="sans" font-size="{size}" font-weight="800" fill="{TEXT}">{t(b)}</text>')
        if sub:
            lines = _wrap(sub)
            col = SOFT if lab in ("RIDING", "CREW") else MUTED
            for j, l in enumerate(lines):
                out.append(f'<text x="{x+20}" y="{y0+th-20 - (len(lines)-1-j)*18}" class="sans" font-size="13" fill="{col}">{t(l)}</text>')
        if lab == "CREW":
            out.append(straw_hat(x + tw - 62, y0 + 42, 0.40))
    out.append(photo_katana(x0 + 196, y0 + 162, 150, -84))
    out.append(crew_flag(372, 262, 1.0))
    qx, qy = 590, 306
    out.append(f'<text x="{qx}" y="{qy}" text-anchor="middle" class="mono" font-size="18" fill="{TEXT}">As long as I live,</text>')
    out.append(f'<text x="{qx}" y="{qy+26}" text-anchor="middle" class="mono" font-size="18" fill="{TEXT}">There are infinite chances.</text>')
    out.append(f'<text x="{qx}" y="{qy+62}" text-anchor="middle" class="mono" font-size="15" fill="{ORANGE}">- Monkey D. Luffy</text>')
    svg("offclock.svg", W, H, "\n".join(out), WIND_CSS + KATANA_CSS + FLAG_CSS)


# ---------------------------------------------------------------- footer
def footer():
    W, H = 1000, 176
    body = f"""
<rect width="{W}" height="{H}" rx="18" fill="{INK}"/>
{wind(40, 4, ORANGE, W, 0.3, 8)}
<text x="{W/2}" y="80" text-anchor="middle" class="serif" font-size="40" font-style="italic" fill="{TEXT}">Veni, vidi, vici.</text>
<text x="{W/2}" y="112" text-anchor="middle" class="mono" font-size="13" fill="{MUTED}" letter-spacing="4">I CAME · I SAW · I CONQUERED</text>
<text x="{W/2}" y="146" text-anchor="middle" class="mono" font-size="15" fill="{ORANGE}">- Elias</text>"""
    svg("footer.svg", W, H, body, WIND_CSS)


if __name__ == "__main__":
    hero(); mantra(); loop(); cards(); stack(); certs(); offclock(); footer()

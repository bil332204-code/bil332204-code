"""Render the animated SVG cards used by README.md.

    python scripts/render_readme_cards.py           # animated cards
    STATIC=1 python scripts/render_readme_cards.py  # final frame only, for screenshots

Reads data/contributions.json (+ data/repos.json if present), writes cards/*.svg.
Everything works inside <img>: inline <style>, CSS keyframes, embedded fonts.
"""
import base64
import datetime as dt
import json
import os
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(os.environ.get("DATA_DIR", ROOT / "data"))
OUT = Path(os.environ.get("OUT_DIR", ROOT / "cards"))
STATIC = os.environ.get("STATIC") == "1"
USER = "bil332204-code"
GH = f"https://github.com/{USER}"

# ── palette ─────────────────────────────────────────────────────────────
C = dict(bg="#0A0E16", panel="#0E1420", line="#1C2536", cell="#151D2B",
         text="#E8EEF7", muted="#8A97AD", dim="#56637A",
         teal="#2DE2B4", violet="#A08FFF", amber="#FFB84D", coral="#FF6B81")
GRAPH = [C["cell"], "#0F4B40", "#138A6E", "#1FC197", C["teal"]]

# ── when each card starts, so the page plays top to bottom ─────────────
T_HERO, T_GRAPH, T_ACT, T_TILES, T_REPOS, T_STACK, T_CERT = 0, 1.0, 1.7, 2.4, 3.1, 3.6, 4.0

# ── content ────────────────────────────────────────────────────────────
TAGLINE = ["Building complete systems where AI, robotics,",
           "software, data and hardware work together."]
FOCUS = "now studying: AI · DSA · Networks · InfoSec · Prob & Stats"

TILES = [
    dict(key="ai", label="AI & ROBOTICS", color=C["teal"], n=4, caption="control modes",
         sub="gesture · emotion · pose · speech", href=f"{GH}/internship-robots"),
    dict(key="sw", label="SOFTWARE", color=C["violet"], n=5, caption="languages I ship in",
         sub="Python · Java · C++ · SQL · JS", href=f"{GH}/fixit-javafx-marketplace"),
    dict(key="data", label="DATA", color=C["amber"], n=8, caption="core entities modeled",
         sub="freelancing marketplace DB", href=f"{GH}/freelancing-marketplace-database"),
]

REPOS = [
    dict(repo="internship-robots", title="AEGIS-JD", color=C["teal"], lang="Python",
         desc="Unified control for the EZ-Robot JD humanoid: gesture, emotion, pose and "
              "speech control with conversational AI, object detection and a "
              "face-recognition security gate.",
         role="Group lead · control modes + final integration",
         chips=["YOLOv8", "MediaPipe", "Flask", "LLaMA"]),
    dict(repo="AiCON-2026-Milaan", title="Milaan", color=C["coral"], lang="Python",
         desc="Checks customers' payment screenshots against a seller's bank or wallet "
              "statement and marks every order SHIP, HOLD or REVIEW, for Instagram and "
              "WhatsApp sellers in Pakistan.",
         role="Built at AiCON'26 · live at milaan.app",
         chips=["FastAPI", "PostgreSQL", "Docker", "Playwright"]),
    dict(repo="fixit-javafx-marketplace", title="FixIt", color=C["violet"], lang="Java",
         desc="Desktop marketplace connecting clients with skilled workers: discovery, "
              "booking workflows, ratings and separate client and worker dashboards.",
         role="Group lead · JavaFX UI, AppController, architecture",
         chips=["Java", "JavaFX", "Maven", "OOP"]),
    dict(repo="freelancing-marketplace-database", title="Freelancing DB", color=C["amber"],
         lang="SQL",
         desc="Relational database for users, freelancers, clients, gigs, skills, orders, "
              "payments and reviews, with analytical reporting.",
         role="DDL/DML, constraints, triggers, SQL debugging",
         chips=["MySQL", "Triggers", "Procedures", "Views"]),
    dict(repo="fractal-cosmos", title="Fractal Cosmos", color="#5BC0FF", lang="JavaScript", wide=True,
         desc="Generative art in the browser: Mandelbrot rendering, recursive trees, "
              "Sierpinski triangles, nested hexagons, seeded randomness and hi-res export.",
         role="Recursion + procedural generation on Canvas",
         chips=["JavaScript", "Canvas", "Recursion"]),
]

STACK = [
    ("languages", ["Python", "Java", "C++", "SQL", "JavaScript"], C["teal"]),
    ("ai / vision", ["OpenCV", "MediaPipe", "DeepFace", "YOLOv8", "LLM integration"], C["coral"]),
    ("development", ["JavaFX", "Flask", "Maven", "Git"], C["violet"]),
    ("databases", ["MySQL", "Firebase / Firestore"], C["amber"]),
    ("other", ["Robotics", "Digital Logic", "System Integration"], C["muted"]),
]

ROBOT = [
    ".-===========-.",
    "/   _       _   \\",
    "|   (o)     (o)   |",
    "|        ^        |",
    "|    \\_______/    |",
    "\\_______________/",
    "__|_____|__",
    ".----'   AEGIS   '----.",
    "| () |  [ J D ]  | () |",
    "|    |  =======  |    |",
    "|____|___________|____|",
    "[____]   |   |   [____]",
    "|   |",
    "_|   |_",
    "[___] [___]",
]

# ── shared svg plumbing ────────────────────────────────────────────────


def font_face(family, file, weight):
    b64 = base64.b64encode((ROOT / "fonts" / file).read_bytes()).decode()
    return (f"@font-face{{font-family:'{family}';font-weight:{weight};"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}")


FONT_FILES = {
    "d": [("Unbounded", "unbounded-700.woff2", 700), ("Unbounded", "unbounded-500.woff2", 500)],
    "m": [("JetBrains Mono", "jetbrains-mono-400.woff2", 400),
          ("JetBrains Mono", "jetbrains-mono-700.woff2", 700)],
}

BASE_CSS = f"""
.d{{font-family:'Unbounded',sans-serif}}
.m{{font-family:'JetBrains Mono',ui-monospace,monospace}}
.pre{{white-space:pre}}
.cu{{opacity:0}}
.fx{{opacity:0}}
"""

ANIM_CSS = """
@keyframes rise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes pop{0%{opacity:0;transform:scale(.2)}70%{opacity:1;transform:scale(1.3)}100%{opacity:1;transform:scale(1)}}
@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes growx{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes swing{0%{opacity:0;transform:translateY(70px) rotate(-7deg)}55%{opacity:1;transform:translateY(-8px) rotate(1.8deg)}78%{transform:translateY(3px) rotate(-.6deg)}100%{opacity:1;transform:none}}
@keyframes shine{0%{opacity:1;transform:translateX(0)}35%{opacity:1;transform:translateX(var(--sx))}35.1%,100%{opacity:0;transform:translateX(var(--sx))}}
@keyframes pulse{0%{opacity:.85;transform:scale(1)}100%{opacity:0;transform:scale(2)}}
@keyframes eyes{0%,88%,100%{fill:#2DE2B4}91%,94%{fill:#1C2536}}
@keyframes caret{50%{opacity:0}}
@keyframes flash{0%,100%{opacity:1}}
@keyframes nudge{0%,100%{transform:translate(0,0)}50%{transform:translate(3px,-3px)}}
@keyframes scan{0%{opacity:0;transform:translateY(0)}10%,85%{opacity:.55}100%{opacity:0;transform:translateY(205px)}}
@keyframes dash{to{stroke-dashoffset:0}}
@keyframes glow{0%,100%{opacity:.35}50%{opacity:.8}}
.a-rise{animation:rise .8s cubic-bezier(.2,.8,.2,1) both}
.a-fade{animation:fade .45s ease both}
.a-pop{animation:pop .45s cubic-bezier(.3,1.5,.5,1) both;transform-box:fill-box;transform-origin:center}
.a-grow{animation:grow .9s cubic-bezier(.2,.8,.2,1) both;transform-box:fill-box;transform-origin:bottom}
.a-growx{animation:growx .9s cubic-bezier(.2,.8,.2,1) both;transform-box:fill-box;transform-origin:left}
.a-swing{animation:swing 1.1s cubic-bezier(.2,.8,.2,1) both;transform-box:fill-box;transform-origin:50% 100%}
.a-shine{animation:shine 6s ease-in-out infinite}
.a-pulse{animation:pulse 2.2s ease-out infinite;transform-box:fill-box;transform-origin:center}
.a-eyes{animation:eyes 4s infinite}
.a-caret{animation:caret 1s steps(1) infinite}
.a-flash{animation-name:flash;animation-timing-function:linear;animation-fill-mode:none}
.a-last{animation:fade .01s both}
.a-nudge{animation:nudge 1.8s ease-in-out infinite}
.a-scan{animation:scan 3.6s linear infinite}
.a-dash{animation:dash 1.4s ease both}
.a-glow{animation:glow 2.4s ease-in-out infinite}
.a-type{transform-box:fill-box;transform-origin:left;animation-name:growx;animation-fill-mode:both}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""


def svg(w, h, body, defs="", css="", fonts="dm", label=""):
    faces = "".join(font_face(*f) for k in fonts for f in FONT_FILES[k])
    style = faces + BASE_CSS + ("" if STATIC else ANIM_CSS) + css
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}">'
            f"<style>{style}</style><defs>{defs}</defs>"
            f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="14" fill="{C["bg"]}" '
            f'stroke="{C["line"]}"/>{body}</svg>')


def d(s):
    """animation-delay style attribute."""
    return f'style="animation-delay:{s:.3f}s"'


def t(x, y, s, cls="m", size=12, fill=None, anchor="start", extra="", weight=None):
    w = f' font-weight="{weight}"' if weight else ""
    return (f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" fill="{fill or C["text"]}"'
            f' text-anchor="{anchor}"{w} {extra}>{escape(s)}</text>')


def arrow(x, y, color, size=10):
    """little north-east arrow drawn as a path (no glyph needed)."""
    s = size
    return (f'<path d="M{x} {y+s} L{x+s} {y} M{x+3} {y} L{x+s} {y} L{x+s} {y+s-3}" '
            f'fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round" '
            f'stroke-linejoin="round"/>')


def count_up(x, y, n, start, size, color, frame=0.07, cls="d", weight=700, anchor="start"):
    """Numbers that count up from zero: one <text> per value, each shown briefly."""
    out = []
    for i in range(n):
        out.append(f'<text x="{x}" y="{y}" class="{cls} cu a-flash" font-size="{size}" '
                   f'font-weight="{weight}" fill="{color}" text-anchor="{anchor}" '
                   f'style="animation-delay:{start + i*frame:.3f}s;animation-duration:{frame:.3f}s">'
                   f'{i}</text>')
    out.append(f'<text x="{x}" y="{y}" class="{cls} a-last" font-size="{size}" font-weight="{weight}"'
               f' fill="{color}" text-anchor="{anchor}" {d(start + n*frame)}>{n:,}</text>')
    return "".join(out)


def shine_band(gid, width, sx, delay, height=400, skew=-20):
    return (f'<linearGradient id="{gid}" x1="0" x2="1" y1="0" y2="0">'
            f'<stop offset="0" stop-color="#fff" stop-opacity="0"/>'
            f'<stop offset=".5" stop-color="#fff" stop-opacity=".55"/>'
            f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>',
            f'<g transform="skewX({skew})"><rect class="fx a-shine" x="-{width+60}" y="-40" '
            f'width="{width}" height="{height}" fill="url(#{gid})" '
            f'style="--sx:{sx}px;animation-delay:{delay:.2f}s"/></g>')


def wrap(s, n):
    lines, cur = [], ""
    for word in s.split():
        if len(cur) + len(word) + (1 if cur else 0) > n:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}" if cur else word
    return lines + ([cur] if cur else [])


# ── data ───────────────────────────────────────────────────────────────


def load():
    p = DATA / "contributions.json"
    days = json.loads(p.read_text())["days"] if p.exists() else []
    days = sorted(days, key=lambda x: x["date"])
    for x in days:
        x["d"] = dt.date.fromisoformat(x["date"])
    rp = DATA / "repos.json"
    repos = {r["name"]: r for r in json.loads(rp.read_text())} if rp.exists() else {}
    return days, repos


def stats(days):
    s = dict(total=0, active=0, cur=0, best=0, busy=None, months=[])
    if not days:
        today = dt.date.today()
        s["months"] = [(today.replace(day=1) - dt.timedelta(days=31 * i)).strftime("%Y-%m")
                       for i in range(11, -1, -1)]
        s["months"] = [(m, 0) for m in s["months"]]
        return s
    year = days[-365:]
    s["total"] = sum(x["count"] for x in year)
    s["active"] = sum(1 for x in year if x["count"])
    run = 0
    for x in days:
        run = run + 1 if x["count"] else 0
        s["best"] = max(s["best"], run)
    tail = days[:-1] if days[-1]["count"] == 0 else days  # today may still be empty
    for x in reversed(tail):
        if not x["count"]:
            break
        s["cur"] += 1
    busy = max(year, key=lambda x: x["count"])
    s["busy"] = busy if busy["count"] else None
    last = days[-1]["d"]
    keys = []
    y, m = last.year, last.month
    for _ in range(12):
        keys.append(f"{y}-{m:02d}")
        y, m = (y, m - 1) if m > 1 else (y - 1, 12)
    keys.reverse()
    per = {k: 0 for k in keys}
    for x in days:
        k = x["date"][:7]
        if k in per:
            per[k] += x["count"]
    s["months"] = list(per.items())
    return s


# ── cards ──────────────────────────────────────────────────────────────


def hero():
    W, H = 840, 300
    defs, body = [], []
    # dotted backdrop
    defs.append(f'<pattern id="dots" width="18" height="18" patternUnits="userSpaceOnUse">'
                f'<circle cx="1" cy="1" r="1" fill="{C["line"]}"/></pattern>')
    defs.append(f'<radialGradient id="halo" cx=".2" cy=".35" r=".7">'
                f'<stop offset="0" stop-color="{C["teal"]}" stop-opacity=".10"/>'
                f'<stop offset="1" stop-color="{C["teal"]}" stop-opacity="0"/></radialGradient>')
    body.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14" fill="url(#dots)" opacity=".55"/>')
    body.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14" fill="url(#halo)" class="a-glow"/>')

    # typed prompt + caret
    prompt = "bilal@seecs:~$ whoami"
    pw = len(prompt) * 7.8
    defs.append(f'<clipPath id="typ"><rect class="a-type" x="32" y="30" width="{pw:.0f}" height="22" '
                f'style="animation-duration:1s;animation-timing-function:steps({len(prompt)});'
                f'animation-delay:.15s"/></clipPath>')
    body.append(f'<g clip-path="url(#typ)">{t(32, 46, prompt, size=13, fill=C["muted"])}</g>')
    body.append(f'<rect class="a-caret" x="{32 + pw + 4:.0f}" y="35" width="8" height="14" fill="{C["teal"]}"/>')

    # name, one line at a time, shine across the second line
    body.append(f'<g class="a-rise" {d(.9)}>{t(30, 112, "Bilal", "d", 54, weight=700)}</g>')
    defs.append(f'<clipPath id="nm"><text x="30" y="172" class="d" font-size="54" font-weight="700">Ahmed</text></clipPath>')
    g, band = shine_band("shn", 70, 520, 2.4, height=300)
    defs.append(g)
    body.append(f'<g class="a-rise" {d(1.08)}>{t(30, 172, "Ahmed", "d", 54, fill=C["teal"], weight=700)}'
                f'<g clip-path="url(#nm)">{band}</g></g>')

    body.append(f'<g class="a-rise" {d(1.3)}>{t(32, 204, "BS Computer Science · NUST SEECS", size=14, weight=700)}</g>')
    for i, line in enumerate(TAGLINE):
        body.append(f'<g class="a-rise" {d(1.42 + i*.1)}>{t(32, 228 + i*18, line, size=12.5, fill=C["muted"])}</g>')

    # status line with pulsing dot
    body.append(f'<g class="a-fade" {d(1.75)}>'
                f'<circle cx="38" cy="272" r="4" fill="{C["teal"]}"/>'
                f'<circle cx="38" cy="272" r="4" fill="none" stroke="{C["teal"]}" class="fx a-pulse"/>'
                f'{t(50, 276, FOCUS, size=11, fill=C["dim"])}</g>')

    # ascii window
    px, py, pw2, ph = 548, 22, 270, 256
    body.append(f'<g class="a-fade" {d(.3)}>'
                f'<rect x="{px}" y="{py}" width="{pw2}" height="{ph}" rx="10" fill="{C["panel"]}" stroke="{C["line"]}"/>'
                f'<path d="M{px} {py+26} H{px+pw2}" stroke="{C["line"]}"/>'
                + "".join(f'<circle cx="{px+16+i*13}" cy="{py+13}" r="4" fill="{c}"/>'
                          for i, c in enumerate([C["coral"], C["amber"], C["teal"]]))
                + t(px + pw2 - 14, py + 17, "aegis-jd.txt", size=10, fill=C["dim"], anchor="end")
                + "</g>")
    defs.append(f'<clipPath id="win"><rect x="{px}" y="{py+27}" width="{pw2}" height="{ph-28}" rx="10"/></clipPath>')
    defs.append(f'<linearGradient id="scan" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0" stop-color="{C["teal"]}" stop-opacity="0"/>'
                f'<stop offset="1" stop-color="{C["teal"]}" stop-opacity=".22"/></linearGradient>')

    width = max(len(r) for r in ROBOT)
    rows = []
    cx = px + pw2 / 2
    for i, r in enumerate(ROBOT):
        row = r.center(width)
        parts = []
        # highlight eyes and the AEGIS / J D badge
        hl = {"(o)": "eye", "AEGIS": "badge", "[ J D ]": "badge"}
        j = 0
        while j < len(row):
            for k, kind in hl.items():
                if row.startswith(k, j):
                    if kind == "eye":
                        parts.append(f'(<tspan class="a-eyes" fill="{C["teal"]}" font-weight="700">o</tspan>)')
                    else:
                        parts.append(f'<tspan fill="{C["teal"]}">{escape(k)}</tspan>')
                    j += len(k)
                    break
            else:
                parts.append(escape(row[j]))
                j += 1
        rows.append(f'<text x="{cx}" y="{py + 48 + i*13.6:.1f}" class="m pre a-fade" xml:space="preserve" '
                    f'font-size="12" fill="{C["muted"]}" text-anchor="middle" {d(.5 + i*.07)}>{"".join(parts)}</text>')
    body.append("".join(rows))
    body.append(f'<g clip-path="url(#win)"><rect class="fx a-scan" x="{px}" y="{py+28}" width="{pw2}" '
                f'height="26" fill="url(#scan)" style="animation-delay:1.8s"/></g>')
    return svg(W, H, "".join(body), "".join(defs), label="Bilal Ahmed, BS Computer Science at NUST SEECS")


def graph(days, s):
    W, H = 840, 214
    cell, gap = 11, 3
    step = cell + gap
    body = [t(28, 38, "contribution graph", "d", 15, weight=500)]
    body.append(f'<text x="{W-28}" y="38" class="m" font-size="12" fill="{C["muted"]}" text-anchor="end">'
                f'<tspan fill="{C["teal"]}" font-weight="700">{s["total"]:,}</tspan> contributions in the last year</text>')
    cols = {}
    if days:
        last = days[-1]["d"]
        end_sun = last - dt.timedelta(days=(last.weekday() + 1) % 7)
        start = end_sun - dt.timedelta(weeks=52)
        for x in days:
            if x["d"] < start:
                continue
            c = (x["d"] - start).days // 7
            cols.setdefault(c, {})[(x["d"].weekday() + 1) % 7] = x
    ncol = 53
    x0 = (W - ncol * step + gap) / 2
    y0 = 78
    cells, months_seen = [], set()
    for c in range(ncol):
        for r in range(7):
            x = cols.get(c, {}).get(r)
            lvl = x["level"] if x else 0
            if x is None and days:
                continue
            cells.append(f'<rect x="{x0 + c*step:.1f}" y="{y0 + r*step}" width="{cell}" height="{cell}" rx="2.5" '
                         f'fill="{GRAPH[lvl]}" class="a-pop" {d(T_GRAPH + .2 + c*.028 + r*.012)}/>')
            if x and r == 0 and x["d"].day <= 7 and c < ncol - 1:
                m = x["d"].strftime("%b")
                if (m, c) not in months_seen:
                    months_seen.add((m, c))
                    body.append(t(round(x0 + c*step, 1), 68, m, size=10, fill=C["dim"]))
    body.append("".join(cells))
    lx = W - 28 - 5*step - 34
    body.append(t(lx - 8, 200, "less", size=10, fill=C["dim"], anchor="end"))
    for i, col in enumerate(GRAPH):
        body.append(f'<rect x="{lx + i*step}" y="191" width="{cell}" height="{cell}" rx="2.5" fill="{col}"/>')
    body.append(t(lx + 5*step + 4, 200, "more", size=10, fill=C["dim"]))
    upd = days[-1]["d"].strftime("%-d %b %Y") if days else "waiting for first run"
    body.append(t(28, 200, f"updated daily · {upd}", size=10, fill=C["dim"]))
    return svg(W, H, "".join(body), label=f"{s['total']} contributions in the last year")


def activity(s):
    W, H = 840, 262
    body = [t(28, 38, "monthly activity", "d", 15, weight=500)]
    months = s["months"]
    vals = [v for _, v in months]
    top = max(vals) if any(vals) else 1
    best = vals.index(max(vals)) if any(vals) else -1
    bx, bw, base, maxh = 36, 520, 212, 128
    slot = bw / len(months)
    body.append(f'<path d="M{bx} {base+.5} H{bx+bw}" stroke="{C["line"]}"/>')
    for i, (k, v) in enumerate(months):
        h = max(3, v / top * maxh) if v else 3
        x = bx + i * slot + (slot - 24) / 2
        col = C["teal"] if i == best else "#24324B"
        body.append(f'<rect x="{x:.1f}" y="{base - h:.1f}" width="24" height="{h:.1f}" rx="4" fill="{col}" '
                    f'class="a-grow" {d(T_ACT + .15 + i*.06)}/>')
        lab = dt.date(int(k[:4]), int(k[5:]), 1).strftime("%b")
        body.append(t(round(x + 12, 1), base + 20, lab, size=10,
                      fill=C["text"] if i == best else C["dim"], anchor="middle"))
        if i == best:
            body.append(f'<g class="a-pop" {d(T_ACT + 1.1)}>'
                        f'{t(round(x + 12, 1), round(base - h - 10, 1), f"{v:,}", size=12, fill=C["teal"], anchor="middle", weight=700)}</g>')
    # stats column
    sx, sw = 588, 224
    body.append(f'<rect x="{sx}" y="58" width="{sw}" height="176" rx="10" fill="{C["panel"]}" stroke="{C["line"]}"/>')
    busy = s["busy"]
    rows = [("total", f'{s["total"]:,}'),
            ("current streak", f'{s["cur"]} day' + ("" if s["cur"] == 1 else "s")),
            ("longest streak", f'{s["best"]} day' + ("" if s["best"] == 1 else "s")),
            ("active days", f'{s["active"]}'),
            ("busiest day", f'{busy["count"]} on {busy["d"].strftime("%-d %b")}' if busy else "-")]
    for i, (k, v) in enumerate(rows):
        y = 90 + i * 33
        body.append(f'<g class="a-rise" {d(T_ACT + .3 + i*.1)}>'
                    f'{t(sx + 16, y, k, size=11, fill=C["muted"])}'
                    f'{t(sx + sw - 16, y + 1, v, "d", 13, fill=C["teal"] if i == 1 else C["text"], anchor="end", weight=500)}'
                    f'</g>')
        if i < len(rows) - 1:
            body.append(f'<path d="M{sx+16} {y+14.5} H{sx+sw-16}" stroke="{C["line"]}"/>')
    return svg(W, H, "".join(body), label="contributions per month and streak stats")


def tile(tl, i):
    W, H = 270, 200
    st = T_TILES + i * .18
    col = tl["color"]
    defs, body = [], []
    defs.append(f'<clipPath id="tc"><rect x="6" y="6" width="{W-12}" height="{H-12}" rx="12"/></clipPath>')
    g, band = shine_band("ts", 60, 420, st + 1.6 + i * .4, height=300)
    defs.append(g)
    inner = [f'<rect x="6.5" y="6.5" width="{W-13}" height="{H-13}" rx="12" fill="{C["panel"]}" stroke="{C["line"]}"/>',
             f'<g clip-path="url(#tc)"><rect x="6" y="6" width="{W-12}" height="3" fill="{col}" class="a-growx" {d(st + .5)}/></g>',
             f'<circle cx="26" cy="36" r="4" fill="{col}"/>',
             t(38, 40, tl["label"], size=11, fill=C["text"], weight=700, extra='letter-spacing="1.5"'),
             # arrow in a ring, ring pulses out
             f'<circle cx="{W-34}" cy="36" r="13" fill="none" stroke="{C["line"]}"/>',
             f'<circle cx="{W-34}" cy="36" r="13" fill="none" stroke="{col}" class="fx a-pulse" {d(st + 1.2)}/>',
             f'<g class="a-nudge">{arrow(W-39, 31, col)}</g>',
             count_up(24, 124, tl["n"], st + .55, 74, col, frame=.09),
             t(26, 152, tl["caption"], size=12.5, weight=700),
             t(26, 174, tl["sub"], size=11, fill=C["muted"]),
             f'<g clip-path="url(#tc)">{band}</g>']
    body.append(f'<g class="a-swing" {d(st)}>{"".join(inner)}</g>')
    # tile svg has no outer border: draw on transparent canvas
    faces = "".join(font_face(*f) for k in "dm" for f in FONT_FILES[k])
    css = faces + BASE_CSS + ("" if STATIC else ANIM_CSS)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="{escape(tl["label"])}: {tl["n"]} {escape(tl["caption"])}">'
            f'<style>{css}</style><defs>{"".join(defs)}</defs>{"".join(body)}</svg>')


def repo_card(r, i, live):
    W, H = (840, 200) if r.get("wide") else (410, 224)
    st = T_REPOS + i * .15
    col = r["color"]
    info = live.get(r["repo"], {})
    lang = info.get("language") or r["lang"]
    lcol = info.get("language_color") or col
    body = [f'<g clip-path="url(#rc)"><rect x="1" y="1" width="{W-2}" height="3" fill="{col}" class="a-growx" {d(st + .3)}/></g>']
    # repo book icon
    body.append(f'<path d="M22 22 h10 a3 3 0 0 1 3 3 v14 a2 2 0 0 0 -2 -2 h-11 z M22 22 v15" fill="none" '
                f'stroke="{C["muted"]}" stroke-width="1.5" stroke-linejoin="round"/>')
    body.append(t(46, 36, r["title"], "d", 15, weight=500))
    body.append(t(46, 54, f"{USER}/{r['repo']}", size=10.5, fill=C["dim"]))
    body.append(f'<g class="a-nudge">{arrow(W-30, 24, col)}</g>')
    lines = wrap(r["desc"], 54 if W < 500 else 116)[:4]
    for j, line in enumerate(lines):
        body.append(t(22, 82 + j*17, line, size=11.2, fill=C["muted"]))
    dy = 0 if W < 500 else -24  # wide card: two description lines, pull the rest up
    body.append(t(22, 156 + dy, r["role"], size=11, fill=col, weight=700))
    cx = 22
    for k, chip in enumerate(r["chips"]):
        w = len(chip) * 6.3 + 20
        body.append(f'<g class="a-pop" {d(st + .5 + k*.07)}>'
                    f'<rect x="{cx:.1f}" y="{168 + dy}" width="{w:.1f}" height="22" rx="11" fill="none" stroke="{C["line"]}"/>'
                    f'{t(round(cx + w/2, 1), 183 + dy, chip, size=10.5, fill=C["text"], anchor="middle")}</g>')
        cx += w + 6
    body.append(f'<circle cx="27" cy="{208 + dy}" r="5" fill="{lcol}"/>')
    body.append(t(38, 212 + dy, lang, size=10.5, fill=C["muted"]))
    meta = []
    if info.get("stars"):
        meta.append(f"{info['stars']} star" + ("" if info["stars"] == 1 else "s"))
    if info.get("pushed_at"):
        meta.append("updated " + dt.date.fromisoformat(info["pushed_at"][:10]).strftime("%b %Y"))
    if meta:
        body.append(t(W - 22, 212 + dy, " · ".join(meta), size=10.5, fill=C["dim"], anchor="end"))
    inner = f'<g class="a-rise" {d(st)}>{"".join(body)}</g>'
    clip = f'<clipPath id="rc"><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14"/></clipPath>'
    return svg(W, H, inner, clip, label=f"{r['title']}: {r['desc']}")


def stack_card():
    W = 840
    H = 64 + len(STACK) * 40
    body = [t(28, 38, "stack", "d", 15, weight=500)]
    n = 0
    for i, (label, items, col) in enumerate(STACK):
        y = 74 + i * 40
        body.append(f'<g class="a-fade" {d(T_STACK + i*.08)}>{t(28, y + 15, label, size=11, fill=C["muted"])}</g>')
        cx = 170
        for item in items:
            w = len(item) * 7 + 30
            body.append(f'<g class="a-pop" {d(T_STACK + .2 + n*.045)}>'
                        f'<rect x="{cx:.1f}" y="{y}" width="{w:.1f}" height="24" rx="12" fill="{C["panel"]}" stroke="{C["line"]}"/>'
                        f'<circle cx="{cx + 13:.1f}" cy="{y + 12}" r="3" fill="{col}"/>'
                        f'{t(round(cx + 21, 1), y + 16, item, size=11, fill=C["text"])}</g>')
            cx += w + 8
            n += 1
    return svg(W, H, "".join(body), label="tech stack")


def cert_card():
    W, H = 840, 96
    body = []
    shield = "M44 24 L62 31 V47 C62 59 54 67 44 72 C34 67 26 59 26 47 V31 Z"
    body.append(f'<path d="{shield}" fill="none" stroke="{C["teal"]}" stroke-width="2" stroke-linejoin="round" '
                f'stroke-dasharray="140" stroke-dashoffset="{0 if STATIC else 140}" class="a-dash" {d(T_CERT)}/>')
    body.append(f'<path d="M36 47 l6 6 l11 -12" fill="none" stroke="{C["teal"]}" stroke-width="2.4" '
                f'stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="30" '
                f'stroke-dashoffset="{0 if STATIC else 30}" class="a-dash" {d(T_CERT + .8)}/>')
    body.append(f'<g class="a-rise" {d(T_CERT + .2)}>'
                f'{t(84, 42, "CISCO NETWORKING ACADEMY · OCT 2026", size=10.5, fill=C["muted"], extra="letter-spacing=\"1.2\"")}'
                f'{t(84, 66, "Introduction to Cybersecurity", "d", 17, weight=500)}</g>')
    body.append(f'<g class="a-fade" {d(T_CERT + .6)}>'
                f'{t(W - 52, 54, "verified on Credly", size=11.5, fill=C["teal"], anchor="end", weight=700)}'
                f'<g class="a-nudge">{arrow(W - 42, 43, C["teal"])}</g></g>')
    return svg(W, H, "".join(body), label="Certification: Cisco Introduction to Cybersecurity, verified on Credly")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    days, live = load()
    s = stats(days)
    files = {"hero.svg": hero(), "graph.svg": graph(days, s), "activity.svg": activity(s),
             "stack.svg": stack_card(), "cert.svg": cert_card()}
    for i, tl in enumerate(TILES):
        files[f"tile-{tl['key']}.svg"] = tile(tl, i)
    for i, r in enumerate(REPOS):
        files[f"repo-{r['repo']}.svg"] = repo_card(r, i, live)
    for name, content in files.items():
        (OUT / name).write_text(content)
    print(f"wrote {len(files)} cards to {OUT} ({'static' if STATIC else 'animated'})")


if __name__ == "__main__":
    main()

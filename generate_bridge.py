from pathlib import Path
import math

ROOT = Path(__file__).resolve().parent
VIEWS = ROOT / "views"
RADIUS = 5

# Clockwise absolute directions in axial coordinates.
DIRECTIONS = [
    ("Forward", 0, -1),
    ("Forstar", 1, -1),
    ("Aftstar", 1, 0),
    ("Aft", 0, 1),
    ("Aftport", -1, 1),
    ("Forport", -1, 0),
]

# COMPLAINT DEPARTMENT:
# Six orientations per cell is elegant architecture until someone has to
# manufacture 546 pages. Apparently that someone is me. Splendid.


def cells():
    result = []
    for q in range(-RADIUS, RADIUS + 1):
        for r in range(-RADIUS, RADIUS + 1):
            s = -q - r
            if max(abs(q), abs(r), abs(s)) <= RADIUS:
                result.append((q, r))
    return result


CELLS = cells()
assert len(CELLS) == 91


def valid(q, r):
    return max(abs(q), abs(r), abs(-q-r)) <= RADIUS


def filename(q, r, heading):
    name = f"q{q:+d}_r{r:+d}_h{heading}.html"
    return "views/" + name.replace("+", "p").replace("-", "m")


def move(q, r, direction_index):
    _, dq, dr = DIRECTIONS[direction_index % 6]
    return q + dq, r + dr


def wall_distances(q, r):
    s = -q-r
    return {
        "Forward": r + RADIUS,
        "Aft": RADIUS - r,
        "Forstar": RADIUS - q,
        "Aftport": q + RADIUS,
        "Aftstar": s + RADIUS,
        "Forport": RADIUS - s,
    }


def pixel_for(q, r, uq, ur, heading):
    dq, dr = q-uq, r-ur
    x = math.sqrt(3) * (dq + dr/2)
    y = 1.5 * dr
    angle = -heading * math.pi / 3
    xr = x*math.cos(angle) - y*math.sin(angle)
    yr = x*math.sin(angle) + y*math.cos(angle)
    return 50 + xr*4.6, 52 + yr*4.6


WALL_ANGLES = {
    "Forward": -90,
    "Forstar": -30,
    "Aftstar": 30,
    "Aft": 90,
    "Aftport": 150,
    "Forport": 210,
}


def wall_style(q, r, name, heading):
    distance = max(0, wall_distances(q, r)[name])
    scale = 1.7 - 0.12*distance
    blur = max(0, (distance-1)*0.55)
    opacity = max(.24, 1-distance*.11)
    angle = math.radians(WALL_ANGLES[name] - heading*60)
    radius = 39
    x = 50 + math.cos(angle)*radius
    y = 50 + math.sin(angle)*radius
    size = max(11, 18*scale)
    return (
        f"left:{x:.2f}%;top:{y:.2f}%;font-size:{size:.1f}px;"
        f"filter:blur({blur:.2f}px);opacity:{opacity:.2f};"
        "transform:translate(-50%,-50%)"
    )


def move_link(q, r, h, relative):
    direction = {"fwd": h, "back": h+3, "left": h-1, "right": h+1}[relative] % 6
    nq, nr = move(q, r, direction)
    if not valid(nq, nr):
        # More complaints: humans insist on walking into walls, and software
        # is somehow expected to have a considered response to this behavior.
        return "../ouch.html"
    return "../" + filename(nq, nr, h)


CSS = r''':root{--bg:#08131c;--panel:#122534;--line:#6b8aa0;--glow:#c8f3ff;--accent:#f4c96b;--danger:#ff8a80;--text:#e9f2f6}*{box-sizing:border-box}html,body{margin:0;min-height:100%;background:var(--bg);color:var(--text);font-family:Arial,Helvetica,sans-serif}body{min-height:100vh;display:grid;place-items:center;overflow:hidden}.bridge{width:min(100vw,1100px);height:min(100vh,760px);position:relative;background:radial-gradient(circle at 50% 55%,#17344a 0,#0a1721 52%,#050b10 100%);border:1px solid #29465a}.viewport{position:absolute;inset:62px 78px 72px;overflow:hidden;clip-path:polygon(25% 0,75% 0,100% 50%,75% 100%,25% 100%,0 50%);border:2px solid var(--line);background:linear-gradient(#102330,#08131c)}.grid{position:absolute;inset:0}.hex{position:absolute;width:42px;height:36px;transform:translate(-50%,-50%);clip-path:polygon(25% 0,75% 0,100% 50%,75% 100%,25% 100%,0 50%);border:1px solid #39566a;background:#102535;opacity:.72}.hex.current{background:#d8f7ff;box-shadow:0 0 18px #c8f3ff;opacity:1}.hex.center{outline:1px solid var(--accent);outline-offset:2px}.heading-arrow{position:absolute;left:50%;top:50%;transform:translate(-50%,-66%);font-size:22px;color:#001018;z-index:5;pointer-events:none}.wall{position:absolute;left:50%;top:50%;transform-origin:center center;color:var(--glow);font-weight:700;letter-spacing:.12em;text-shadow:0 0 8px rgba(200,243,255,.45);white-space:nowrap;pointer-events:none}.status{position:absolute;left:50%;top:14px;transform:translateX(-50%);font-size:13px;letter-spacing:.08em;color:#a9c2d0}.control{position:absolute;display:grid;place-items:center;width:54px;height:54px;border:1px solid #63879c;background:#0d1d28;color:#dff8ff;text-decoration:none;font-size:28px;line-height:1;user-select:none}.control:hover{background:#173247}.fwd{left:50%;top:4px;transform:translateX(-50%)}.back{left:50%;bottom:6px;transform:translateX(-50%)}.left{left:8px;top:50%;transform:translateY(-50%)}.right{right:8px;top:50%;transform:translateY(-50%)}.tl1{left:8px;top:8px}.tr1{right:8px;top:8px}.bl2{left:8px;bottom:8px}.br2{right:8px;bottom:8px}.caption{position:absolute;bottom:43px;left:50%;transform:translateX(-50%);font-size:12px;color:#89a5b6}.turbolift{position:absolute;padding:5px 8px;border:1px solid #788894;color:#d8e1e7;font-size:10px;background:#17222a}@media(max-width:700px){.bridge{height:100vh}.viewport{inset:68px 64px 78px}.control{width:46px;height:46px;font-size:24px}.hex{width:34px;height:29px}}'''


OUCH = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>OUCH!</title>
<style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#12090a;color:#fff;font-family:Arial,Helvetica,sans-serif}main{width:min(720px,90vw);text-align:center;border:2px solid #ff8a80;padding:2rem;background:#221012}h1{font-size:clamp(4rem,14vw,9rem);margin:0;color:#ff8a80}p{font-size:1.35rem}.voice{margin-top:2rem;font-style:italic;color:#ddd}.choices{display:grid;gap:1rem;margin-top:2rem}button{font:inherit;padding:1rem;border:1px solid #ddd;background:#161616;color:white;cursor:pointer}button:hover{background:#292929}</style></head>
<body><main><h1>OUCH!</h1><p>That fuckin' hurt!</p><p class="voice">A disembodied voice says: “Report to sickbay for evaluation.”</p><div class="choices"><button onclick="history.back()">I'll be okay, sir!</button><button onclick="history.back()">Why did you have to make these walls so solid?</button></div></main></body></html>'''


def build():
    VIEWS.mkdir(exist_ok=True)
    (ROOT / "bridge.css").write_text(CSS, encoding="utf-8")
    (ROOT / "ouch.html").write_text(OUCH, encoding="utf-8")

    for q, r in CELLS:
        for h in range(6):
            hexes = []
            for cq, cr in CELLS:
                x, y = pixel_for(cq, cr, q, r, h)
                classes = ["hex"]
                if (cq, cr) == (q, r): classes.append("current")
                if (cq, cr) == (0, 0): classes.append("center")
                hexes.append(f'<div class="{" ".join(classes)}" style="left:{x:.2f}%;top:{y:.2f}%"></div>')

            walls = [
                f'<div class="wall" style="{wall_style(q,r,name,h)}">{name.upper()}</div>'
                for name in ["Forward","Forstar","Aftstar","Aft","Aftport","Forport"]
            ]
            tx, ty = pixel_for(0, RADIUS, q, r, h)
            turbolift = f'<div class="turbolift" style="left:{tx:.2f}%;top:{ty:.2f}%;transform:translate(-50%,-50%)">TURBOLIFT</div>'

            doc = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Bridge — {q},{r} — {DIRECTIONS[h][0]}</title><link rel="stylesheet" href="../bridge.css"></head><body>
<main class="bridge"><div class="status">POSITION {q},{r} · FACING {DIRECTIONS[h][0].upper()}</div>
<a class="control fwd" href="{move_link(q,r,h,'fwd')}" aria-label="Move forward">↑</a>
<a class="control back" href="{move_link(q,r,h,'back')}" aria-label="Move backward">↓</a>
<a class="control left" href="{move_link(q,r,h,'left')}" aria-label="Move left">←</a>
<a class="control right" href="{move_link(q,r,h,'right')}" aria-label="Move right">→</a>
<a class="control tl1" href="../{filename(q,r,(h-1)%6)}" aria-label="Turn one orientation left">↶</a>
<a class="control tr1" href="../{filename(q,r,(h+1)%6)}" aria-label="Turn one orientation right">↷</a>
<a class="control bl2" href="../{filename(q,r,(h-2)%6)}" aria-label="Turn two orientations left">⟲</a>
<a class="control br2" href="../{filename(q,r,(h+2)%6)}" aria-label="Turn two orientations right">⟳</a>
<section class="viewport" aria-label="Bridge view"><div class="grid">{"".join(hexes)}<div class="heading-arrow">▲</div>{"".join(walls)}{turbolift}</div></section>
<div class="caption">Grand hexagon: radius 5 · 91 positions · six orientations</div></main></body></html>'''
            (ROOT / filename(q, r, h)).write_text(doc, encoding="utf-8")

    entry = filename(0, RADIUS, 0)
    index = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Our Lovely System — Bridge</title><style>body{{margin:0;min-height:100vh;display:grid;place-items:center;background:#071018;color:#eaf5fa;font-family:Arial,Helvetica,sans-serif}}main{{text-align:center}}a{{display:inline-block;margin-top:2rem;padding:1rem 1.4rem;border:1px solid #9fc6d8;color:#eaf5fa;text-decoration:none;background:#10212d}}</style></head><body><main><h1>BRIDGE</h1><p>The turbolift doors are open.</p><a href="{entry}">Enter the bridge</a></main></body></html>'''
    (ROOT / "index.html").write_text(index, encoding="utf-8")
    (ROOT / "GENERATION.txt").write_text(
        "Generated static artifact: 91 positions × 6 orientations = 546 bridge view pages.\n",
        encoding="utf-8",
    )

    count = len(list(VIEWS.glob("*.html")))
    assert count == 546, count
    print(f"Generated {count} bridge views.")


if __name__ == "__main__":
    build()

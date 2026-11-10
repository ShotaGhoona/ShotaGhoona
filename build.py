"""Generate the animated SVGs used by the profile README.

Run:  python3 build.py   -> writes assets/*.svg (dark + light variants)
GitHub shows README images through <img>, so everything here is plain SVG + CSS
animation: no scripts, no web fonts.
"""
import math
from pathlib import Path

OUT = Path(__file__).parent / "assets"
OUT.mkdir(exist_ok=True)

THEMES = {
    "dark": dict(bg="#0d1117", fg="#e6edf3", sub="#7d8590", line="#30363d",
                 accent="#e3b341", dot="#238636", dot0="#161b22"),
    "light": dict(bg="#ffffff", fg="#1f2328", sub="#656d76", line="#d0d7de",
                  accent="#9a6700", dot="#2da44e", dot0="#ebedf0"),
}

SERIF = "'Iowan Old Style','Palatino Linotype','Hiragino Mincho ProN','Yu Mincho',Georgia,serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Hiragino Sans',sans-serif"


# ---------------------------------------------------------------- header
def header(t):
    W, H = 840, 300
    # contribution-style dot field on the right; a diagonal wave lights it up
    cols, rows, gap, r = 16, 7, 15, 5
    gx, gy = W - 40 - cols * gap, 70
    # cells that spell nothing in particular but feel like a real commit graph
    dots = []
    for c in range(cols):
        for rr in range(rows):
            seed = (c * 7 + rr * 13 + c * rr) % 11
            lvl = 0 if seed < 4 else (1 if seed < 7 else (2 if seed < 9 else 3))
            op = [0, .35, .65, 1][lvl]
            delay = (c + rr) * 0.06
            dots.append(
                f'<rect class="d" x="{gx + c*gap}" y="{gy + rr*gap}" width="{2*r+1}" height="{2*r+1}" rx="2.5" '
                f'style="--o:{op};animation-delay:{delay:.2f}s,{2.4+delay:.2f}s"/>'
            )
    dots = "\n    ".join(dots)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <style>
    .bg {{ fill:{t['bg']}; }}
    .rule {{ stroke:{t['line']}; stroke-width:1; stroke-dasharray:800; stroke-dashoffset:800;
             animation:draw 1.4s .2s cubic-bezier(.6,0,.2,1) forwards; }}
    .kicker {{ font:600 11px {SANS}; letter-spacing:.32em; fill:{t['accent']};
               opacity:0; animation:fade .8s .3s forwards; }}
    .name {{ font:400 64px {SERIF}; letter-spacing:-.01em; fill:transparent; stroke:{t['fg']};
             stroke-width:.8; stroke-dasharray:420; stroke-dashoffset:420;
             animation:ink 2.2s .5s cubic-bezier(.5,0,.2,1) forwards, fill .9s 2.2s forwards; }}
    .ja {{ font:400 15px {SERIF}; letter-spacing:.5em; fill:{t['sub']}; opacity:0; animation:fade 1s 2.4s forwards; }}
    .meta {{ font:400 12.5px {MONO}; fill:{t['sub']}; opacity:0; animation:fade .8s 2.8s forwards; }}
    .meta b {{ font-weight:400; fill:{t['fg']}; }}
    .cur {{ fill:{t['accent']}; animation:blink 1.06s steps(1) infinite; }}
    .d {{ fill:{t['dot']}; opacity:0; animation:pop .5s ease-out forwards, breathe 4.8s ease-in-out infinite; }}
    .d0 {{ fill:{t['dot0']}; }}
    @keyframes draw  {{ to {{ stroke-dashoffset:0; }} }}
    @keyframes ink   {{ to {{ stroke-dashoffset:0; }} }}
    @keyframes fill  {{ to {{ fill:{t['fg']}; stroke-width:0; }} }}
    @keyframes fade  {{ to {{ opacity:1; }} }}
    @keyframes blink {{ 50% {{ opacity:0; }} }}
    @keyframes pop   {{ from {{ opacity:0; transform:translateY(4px); }} to {{ opacity:var(--o); transform:none; }} }}
    @keyframes breathe {{ 0%,100% {{ opacity:var(--o); }} 50% {{ opacity:calc(var(--o) * .35 + .1); }} }}
    @media (prefers-reduced-motion: reduce) {{ * {{ animation-duration:0s !important; animation-delay:0s !important; }} }}
  </style>
  <rect class="bg" width="{W}" height="{H}" rx="12"/>

  <text class="kicker" x="40" y="64">PRODUCT MANAGER — ARCHAIVE / STARUP</text>
  <text class="name" x="36" y="150">Shota Yamashita</text>
  <text class="ja" x="40" y="186">山下 翔大</text>

  <line class="rule" x1="40" y1="222" x2="{W-40}" y2="222"/>

  <text class="meta" x="40" y="256">~/kyoto <b>$</b> whoami <tspan dx="4">— 現場とエンジニアと経営のあいだを訳して、プロダクトにする人</tspan></text>
  <rect class="cur" x="{W-52}" y="245" width="8" height="15"/>

  <g>
    {"".join(f'<rect class="d0" x="{gx + c*gap}" y="{gy + rr*gap}" width="{2*r+1}" height="{2*r+1}" rx="2.5"/>' for c in range(cols) for rr in range(rows))}
    {dots}
  </g>
</svg>'''


# ---------------------------------------------------------------- git log timeline
COMMITS = [
    ("HEAD -> main", "2026.06", "ARCHAIVE のプロダクトマネージャーに"),
    (None,           "2025.10", "ARCHAIVE Quote のフロントエンドを担当"),
    ("merge",        "2024.11", "Merge branch 'starup' — STARUP に参加"),
    (None,           "2024.04", "インドに交換留学。9,000 km をバックパックで"),
    (None,           "2024.02", "1,200 人規模の学生フェスを 40 人で運営"),
    ("pivot",        "2023.06", "ChatGPT に出会い、デザインから AI エンジニアリングへ"),
    ("tag: v1.0",    "2020.04", "京都大学 工学部 建築学科に入学"),
]
HASHES = ["5897dea", "c41e2b9", "9a0f7d3", "e1b4c8f", "a6e8b4d", "d3f7a21", "0b2a5e1"]


def timeline(t):
    W, row, top = 840, 34, 64
    H = top + row * len(COMMITS) + 30
    lines = []
    for i, ((ref, date, msg), h) in enumerate(zip(COMMITS, HASHES)):
        y = top + i * row
        d = 0.35 + i * 0.28
        badge = ""
        if ref:
            col = t['accent'] if ref.startswith("HEAD") else t['sub']
            badge = f'<tspan fill="{col}">({ref})</tspan> '
        lines.append(f'''
  <g class="c" style="animation-delay:{d:.2f}s">
    <circle cx="52" cy="{y-4}" r="{5 if i==0 else 4}" class="{'head' if i==0 else 'node'}"/>
    <text x="72" y="{y}" class="mono"><tspan class="hash">{h}</tspan>  <tspan class="date">{date}</tspan>  {badge}<tspan class="msg">{msg}</tspan></text>
  </g>''')
    # branch lane for the STARUP merge (2024.11 -> 2025.10 -> 2026.06 sit on a side lane)
    y0, y2 = top - 4, top + 2 * row - 4
    branch = f'<path class="lane2" d="M52 {y2} C 52 {y2-14}, 72 {y2-18}, 72 {y2-row} L72 {y0+12} C72 {y0+4}, 60 {y0}, 52 {y0}"/>'

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <style>
    .bg {{ fill:{t['bg']}; }}
    .title {{ font:600 11px {SANS}; letter-spacing:.32em; fill:{t['accent']}; }}
    .cmd {{ font:400 12.5px {MONO}; fill:{t['sub']}; }}
    .mono {{ font:400 13px {MONO}; fill:{t['fg']}; }}
    .hash {{ fill:{t['accent']}; }}
    .date {{ fill:{t['sub']}; }}
    .lane {{ stroke:{t['line']}; stroke-width:2; fill:none; stroke-dasharray:400; stroke-dashoffset:400;
             animation:draw 2.4s .2s ease-in-out forwards; }}
    .lane2 {{ stroke:{t['accent']}; stroke-opacity:.5; stroke-width:2; fill:none; stroke-dasharray:200; stroke-dashoffset:200;
              animation:draw 1.2s 1.4s ease-in-out forwards; }}
    .node {{ fill:{t['bg']}; stroke:{t['sub']}; stroke-width:2; }}
    .head {{ fill:{t['accent']}; }}
    .c {{ opacity:0; animation:in .5s ease-out forwards; }}
    .typing {{ font:400 12.5px {MONO}; fill:{t['sub']}; }}
    .cur {{ fill:{t['accent']}; animation:blink 1.06s steps(1) infinite; }}
    @keyframes draw {{ to {{ stroke-dashoffset:0; }} }}
    @keyframes in {{ from {{ opacity:0; transform:translateX(-6px); }} to {{ opacity:1; transform:none; }} }}
    @keyframes blink {{ 50% {{ opacity:0; }} }}
    @media (prefers-reduced-motion: reduce) {{ * {{ animation-duration:0s !important; animation-delay:0s !important; }} }}
  </style>
  <rect class="bg" width="{W}" height="{H}" rx="12"/>
  <text class="title" x="40" y="34">TIMELINE</text>
  <text class="cmd" x="{W-40}" y="34" text-anchor="end">$ git log --graph --oneline shota</text>
  <line class="lane" x1="52" y1="{top-4}" x2="52" y2="{top + row*(len(COMMITS)-1) - 4}"/>

  {"".join(lines)}
</svg>'''


for name, t in THEMES.items():
    (OUT / f"header-{name}.svg").write_text(header(t), encoding="utf-8")
    (OUT / f"timeline-{name}.svg").write_text(timeline(t), encoding="utf-8")
print("written:", sorted(p.name for p in OUT.iterdir()))

#!/usr/bin/env python3
"""
Generates today's animated profile banner (light_mode.svg / dark_mode.svg).
Run daily via GitHub Actions so the date stays current; the animations
themselves loop continuously in the browser regardless of when this ran.

The banner is styled like a hacker terminal: Matrix-style falling code in
the background, a moving scanline, a glitching name, animated data streams
and a scrolling tech ticker.
"""

import random
from datetime import datetime
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")

ROLES = [
    "Backend Engineer in training",
    "Spring Boot / Kafka / Distributed Systems",
    "CSE (AI/ML) @ RIT Bengaluru",
]

TICKER_ITEMS = [
    "Java", "Spring Boot", "Kafka", "gRPC", "PostgreSQL",
    "Redis", "Docker", "React", "Spring AI", "AWS",
]

MONO = "'Fira Code', 'JetBrains Mono', Consolas, monospace"

WIDTH, HEIGHT = 760, 210

# Character set for the Matrix rain / data streams.
GLYPHS = "01<>/{}[]$#%&*+=;:|10ｱｲｳｴｵｶｷｸ01ABCDEF9876"


def _esc(ch):
    return {"<": "&lt;", ">": "&gt;", "&": "&amp;"}.get(ch, ch)


def build_matrix_rain(rng, fg, accent):
    """Vertical columns of falling glyphs, staggered so they look alive."""
    cols = []
    x = 8
    col_gap = 15
    idx = 0
    while x < WIDTH - 4:
        dur = rng.uniform(3.5, 8.5)
        delay = -rng.uniform(0, dur)
        font = rng.choice([11, 12, 13])
        chars = [rng.choice(GLYPHS) for _ in range(rng.randint(14, 22))]
        # Break the column into tspans so the leading glyph can glow brighter.
        spans = []
        for j, ch in enumerate(chars):
            fill = accent if j == 0 else fg
            spans.append(
                f'<tspan x="{x}" dy="{font + 2}" fill="{fill}">{_esc(ch)}</tspan>'
            )
        cols.append(
            f'<text class="rain" font-size="{font}" '
            f'style="animation-duration:{dur:.2f}s;animation-delay:{delay:.2f}s">'
            f'{"".join(spans)}</text>'
        )
        x += col_gap + rng.randint(0, 6)
        idx += 1
    return "\n".join(cols)


def build_streams(rng, subtle):
    """A few horizontal hex/binary streams sliding across the panel."""
    lines = []
    ys = [98, 132, 152]
    for k, y in enumerate(ys):
        chunk = " ".join(
            "".join(rng.choice("0123456789ABCDEF") for _ in range(2))
            for _ in range(28)
        )
        dur = rng.uniform(14, 22)
        direction = "-50%" if k % 2 == 0 else "50%"
        lines.append(f'''
  <g clip-path="url(#panel-clip)" opacity="0.25">
    <text y="{y}" class="stream" font-size="11"
      style="animation:stream-{k} {dur:.1f}s linear infinite">{chunk}    {chunk}</text>
  </g>
  <style>
    @keyframes stream-{k} {{
      from {{ transform: translateX(0); }}
      to {{ transform: translateX({direction}); }}
    }}
  </style>''')
    return "".join(lines)


def build_svg(theme: str) -> str:
    # Deterministic-ish per run but varied layout; seed on the day so the
    # background reshuffles daily without flickering within a single render.
    now = datetime.now(IST)
    rng = random.Random(now.strftime("%Y%m%d") + theme)
    date_str = now.strftime("%A, %d %B %Y")

    # Terminal theme is identical for both light and dark GitHub themes:
    # this banner should always read like a hacker terminal window.
    bg = "#050805"
    titlebar = "#0d130d"
    fg = "#2fbf3f"
    accent = "#00ff41"
    bright = "#7dff9a"
    subtle = "#4f7a4f"
    border = "#153015"

    slot = 4  # seconds per role
    cycle = slot * len(ROLES)

    role_css = []
    role_svg = []
    for i, role in enumerate(ROLES):
        start = (i * 100) / len(ROLES)
        end = ((i + 1) * 100) / len(ROLES)
        fade = 100 / len(ROLES) * 0.12
        role_css.append(f'''
    .role-{i} {{
      animation: role-{i}-cycle {cycle}s ease-in-out infinite;
    }}
    @keyframes role-{i}-cycle {{
      0% {{ opacity: 0; }}
      {start:.2f}% {{ opacity: 0; }}
      {start + fade:.2f}% {{ opacity: 1; }}
      {end - fade:.2f}% {{ opacity: 1; }}
      {end:.2f}% {{ opacity: 0; }}
      100% {{ opacity: 0; }}
    }}''')
        role_svg.append(f'<text x="30" y="150" class="role role-{i}">&gt; {role}</text>')

    ticker_text = "    /    ".join(TICKER_ITEMS)
    ticker_full = f"{ticker_text}    /    {ticker_text}"

    matrix = build_matrix_rain(rng, fg, accent)
    streams = build_streams(rng, subtle)

    return f'''<svg width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" xmlns="http://www.w3.org/2000/svg">
  <style>
    .bg {{ fill: {bg}; }}
    .titlebar {{ fill: {titlebar}; }}
    .border {{ fill: none; stroke: {border}; stroke-width: 1; }}
    .titletext {{ font-family: {MONO}; font-size: 12px; fill: {subtle}; }}
    .prompt {{ font-family: {MONO}; font-size: 14px; fill: {subtle}; }}
    .name {{
      font-family: {MONO};
      font-size: 28px;
      font-weight: 700;
      fill: {accent};
    }}
    .role {{ font-family: {MONO}; font-size: 16px; fill: {bright}; opacity: 0; }}
    .meta {{ font-family: {MONO}; font-size: 13px; fill: {subtle}; }}
    .rain {{
      font-family: {MONO};
      fill: {fg};
      opacity: 0.28;
      animation-name: fall;
      animation-timing-function: linear;
      animation-iteration-count: infinite;
    }}
    @keyframes fall {{
      0%   {{ transform: translateY(-115%); opacity: 0; }}
      8%   {{ opacity: 0.30; }}
      92%  {{ opacity: 0.30; }}
      100% {{ transform: translateY(105%); opacity: 0; }}
    }}
    .stream {{ font-family: {MONO}; fill: {subtle}; }}
    .ticker-track {{
      font-family: {MONO};
      font-size: 13px;
      fill: {subtle};
      animation: scroll 18s linear infinite;
    }}
    @keyframes scroll {{
      from {{ transform: translateX(0); }}
      to {{ transform: translateX(-50%); }}
    }}
    .cursor {{ fill: {accent}; animation: blink 1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity: 0; }} }}
    /* Glitch: quick horizontal jitter + colour split on the name. */
    .glitch {{ animation: glitch 4.5s steps(1) infinite; }}
    @keyframes glitch {{
      0%, 92%, 100% {{ transform: translate(0,0); }}
      93% {{ transform: translate(-2px, 1px); }}
      94% {{ transform: translate(2px, -1px); }}
      95% {{ transform: translate(-1px, 0); }}
      96% {{ transform: translate(1px, 1px); }}
      97% {{ transform: translate(0, 0); }}
    }}
    .glitch-r {{ fill: #ff2e88; opacity: 0; mix-blend-mode: screen; animation: gsplit 4.5s steps(1) infinite; }}
    .glitch-b {{ fill: #22d3ff; opacity: 0; mix-blend-mode: screen; animation: gsplit 4.5s steps(1) infinite; animation-delay: 0.04s; }}
    @keyframes gsplit {{
      0%, 92%, 100% {{ opacity: 0; transform: translate(0,0); }}
      93% {{ opacity: 0.8; transform: translate(-3px, 0); }}
      95% {{ opacity: 0.8; transform: translate(3px, 0); }}
      97% {{ opacity: 0; transform: translate(0,0); }}
    }}
    .scanline {{ animation: scan 6s linear infinite; }}
    @keyframes scan {{
      from {{ transform: translateY(-10px); }}
      to {{ transform: translateY({HEIGHT}px); }}
    }}
    .flicker {{ animation: flicker 3.5s ease-in-out infinite; }}
    @keyframes flicker {{
      0%, 100% {{ opacity: 1; }}
      48% {{ opacity: 1; }}
      50% {{ opacity: 0.82; }}
      52% {{ opacity: 1; }}
      70% {{ opacity: 0.9; }}
    }}
    {"".join(role_css)}
  </style>

  <defs>
    <clipPath id="panel-clip"><rect x="0" y="30" width="{WIDTH}" height="{HEIGHT - 30}" /></clipPath>
    <clipPath id="ticker-clip"><rect x="30" y="42" width="700" height="18" /></clipPath>
    <radialGradient id="vign" cx="50%" cy="45%" r="75%">
      <stop offset="60%" stop-color="{bg}" stop-opacity="0" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0.55" />
    </radialGradient>
    <linearGradient id="scanfade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{accent}" stop-opacity="0" />
      <stop offset="50%" stop-color="{accent}" stop-opacity="0.18" />
      <stop offset="100%" stop-color="{accent}" stop-opacity="0" />
    </linearGradient>
  </defs>

  <rect class="bg" width="{WIDTH}" height="{HEIGHT}" rx="10" />

  <!-- Matrix rain + data streams behind the content -->
  <g clip-path="url(#panel-clip)">
{matrix}
  </g>
  {streams}

  <!-- CRT vignette + moving scanline -->
  <rect x="0" y="30" width="{WIDTH}" height="{HEIGHT - 30}" fill="url(#vign)" pointer-events="none" />
  <g clip-path="url(#panel-clip)">
    <rect class="scanline" x="0" y="0" width="{WIDTH}" height="14" fill="url(#scanfade)" />
  </g>

  <!-- Title bar -->
  <path class="titlebar" d="M0 10 A10 10 0 0 1 10 0 L750 0 A10 10 0 0 1 760 10 L760 30 L0 30 Z" />
  <circle cx="22" cy="15" r="6" fill="#ff5f56" />
  <circle cx="42" cy="15" r="6" fill="#ffbd2e" />
  <circle cx="62" cy="15" r="6" fill="#27c93f" />
  <text x="380" y="19" text-anchor="middle" class="titletext">shreyas@bengaluru: ~ — root access granted</text>
  <rect class="border" x="0.5" y="0.5" width="759" height="209" rx="10" />

  <!-- Scrolling tech ticker -->
  <g clip-path="url(#ticker-clip)">
    <text x="30" y="55" class="ticker-track">{ticker_full}</text>
  </g>

  <!-- Foreground content -->
  <g class="flicker">
    <text x="30" y="88" class="prompt">$ whoami</text>
    <g class="glitch">
      <text x="30" y="120" class="glitch-b name">Shreyas</text>
      <text x="30" y="120" class="glitch-r name">Shreyas</text>
      <text x="30" y="120" class="name">Shreyas<tspan class="cursor">_</tspan></text>
    </g>

    {"".join(role_svg)}

    <line x1="30" y1="166" x2="730" y2="166" stroke="{border}" stroke-width="1" />
    <text x="30" y="188" class="meta">Bengaluru, India   |   Software Engineer Intern, Hampi Labs</text>
    <text x="30" y="206" class="meta">{date_str}</text>
  </g>
</svg>
'''


def main():
    with open("light_mode.svg", "w", encoding="utf-8") as f:
        f.write(build_svg("light"))
    with open("dark_mode.svg", "w", encoding="utf-8") as f:
        f.write(build_svg("dark"))
    print("Generated light_mode.svg and dark_mode.svg")


if __name__ == "__main__":
    main()

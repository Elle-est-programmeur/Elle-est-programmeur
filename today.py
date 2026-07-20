#!/usr/bin/env python3
"""
Generates today's animated profile banner (light_mode.svg / dark_mode.svg).
Run daily via GitHub Actions so the date stays current; the animations
themselves loop continuously in the browser regardless of when this ran.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")

ROLES = [
    "Backend Engineer in training",
    "Spring Boot / Kafka / Distributed Systems",
    "CSE (AI/ML) @ RIT Bengaluru",
    "650+ DSA problems solved",
]

TICKER_ITEMS = [
    "Java", "Spring Boot", "Kafka", "gRPC", "PostgreSQL",
    "Redis", "Docker", "React", "Spring AI", "AWS",
]

MONO = "'Fira Code', 'JetBrains Mono', Consolas, monospace"


def build_svg(theme: str) -> str:
    now = datetime.now(IST)
    date_str = now.strftime("%A, %d %B %Y")

    # Terminal theme is identical for both light and dark GitHub themes:
    # this banner should always read like a terminal window.
    bg = "#0a0e0a"
    titlebar = "#161c16"
    fg = "#39ff14"
    accent = "#00ff41"
    subtle = "#6b8f6b"
    border = "#1f2a1f"

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

    return f'''<svg width="760" height="210" viewBox="0 0 760 210" xmlns="http://www.w3.org/2000/svg">
  <style>
    .bg {{ fill: {bg}; }}
    .titlebar {{ fill: {titlebar}; }}
    .border {{ fill: none; stroke: {border}; stroke-width: 1; }}
    .titletext {{
      font-family: {MONO};
      font-size: 12px;
      fill: {subtle};
    }}
    .prompt {{
      font-family: {MONO};
      font-size: 14px;
      fill: {subtle};
    }}
    .name {{
      font-family: {MONO};
      font-size: 28px;
      font-weight: 700;
      fill: {fg};
    }}
    .role {{
      font-family: {MONO};
      font-size: 16px;
      fill: {accent};
      opacity: 0;
    }}
    .meta {{
      font-family: {MONO};
      font-size: 13px;
      fill: {subtle};
    }}
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
    .cursor {{
      fill: {accent};
      animation: blink 1s steps(1) infinite;
    }}
    @keyframes blink {{
      50% {{ opacity: 0; }}
    }}
    {"".join(role_css)}
  </style>

  <rect class="bg" width="760" height="210" rx="10" />
  <path class="titlebar" d="M0 10 A10 10 0 0 1 10 0 L750 0 A10 10 0 0 1 760 10 L760 30 L0 30 Z" />
  <circle cx="22" cy="15" r="6" fill="#ff5f56" />
  <circle cx="42" cy="15" r="6" fill="#ffbd2e" />
  <circle cx="62" cy="15" r="6" fill="#27c93f" />
  <text x="380" y="19" text-anchor="middle" class="titletext">shreyas@bengaluru: ~</text>
  <rect class="border" x="0.5" y="0.5" width="759" height="209" rx="10" />

  <clipPath id="ticker-clip">
    <rect x="30" y="42" width="700" height="18" />
  </clipPath>
  <g clip-path="url(#ticker-clip)">
    <text x="30" y="55" class="ticker-track">{ticker_full}</text>
  </g>

  <text x="30" y="88" class="prompt">$ whoami</text>
  <text x="30" y="120" class="name">Shreyas<tspan class="cursor">_</tspan></text>

  {"".join(role_svg)}

  <line x1="30" y1="166" x2="730" y2="166" stroke="{border}" stroke-width="1" />

  <text x="30" y="188" class="meta">Bengaluru, India   |   Software Engineer Intern, Hampi Labs</text>
  <text x="30" y="206" class="meta">{date_str}</text>
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

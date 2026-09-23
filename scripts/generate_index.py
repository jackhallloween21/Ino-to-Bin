#!/usr/bin/env python3
"""Build docs/index.html listing whatever .bin files are in docs/downloads/."""

from datetime import datetime, timezone
from pathlib import Path

DOWNLOADS_DIR = Path("docs/downloads")
OUTPUT_FILE = Path("docs/index.html")

ROW_TEMPLATE = """
        <tr>
          <td>{name}</td>
          <td>{size_kb} KB</td>
          <td><a href="downloads/{filename}">Download .bin</a></td>
        </tr>"""

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Firmware builds</title>
<style>
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: #10141a; color: #eef1f5; margin: 0; padding: 32px 16px;
  }}
  .wrap {{ max-width: 720px; margin: 0 auto; }}
  h1 {{ font-size: 20px; margin-bottom: 4px; }}
  .sub {{ color: #8a94a3; font-size: 13px; margin-bottom: 24px; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th, td {{ text-align: left; padding: 10px 8px; border-bottom: 1px solid rgba(255,255,255,0.08); font-size: 14px; }}
  th {{ color: #8a94a3; font-weight: 500; font-size: 12px; text-transform: uppercase; }}
  a {{ color: #5ecbff; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  .empty {{ color: #8a94a3; font-size: 14px; }}
</style>
</head>
<body>
<div class="wrap">
  <h1>Firmware builds</h1>
  <div class="sub">Auto-built from sketches/ by GitHub Actions · last build {timestamp} UTC</div>
  <table>
    <thead><tr><th>Build</th><th>Size</th><th>File</th></tr></thead>
    <tbody>{rows}
    </tbody>
  </table>
</div>
</body>
</html>
"""


def main() -> None:
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    bin_files = sorted(DOWNLOADS_DIR.glob("*.bin"))

    if bin_files:
        rows = "".join(
            ROW_TEMPLATE.format(
                name=f.stem,
                size_kb=round(f.stat().st_size / 1024, 1),
                filename=f.name,
            )
            for f in bin_files
        )
    else:
        rows = '\n        <tr><td colspan="3" class="empty">No builds yet.</td></tr>'

    html = PAGE_TEMPLATE.format(
        rows=rows,
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
    )
    OUTPUT_FILE.write_text(html)
    print(f"[generate_index] wrote {OUTPUT_FILE} with {len(bin_files)} build(s)")


if __name__ == "__main__":
    main()

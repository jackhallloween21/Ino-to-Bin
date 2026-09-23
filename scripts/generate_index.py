#!/usr/bin/env python3
"""Build docs/index.html with the upload form and a list of .bin downloads."""

from pathlib import Path

DOWNLOADS_DIR = Path("docs/downloads")
OUTPUT_FILE = Path("docs/index.html")


def build_download_list() -> str:
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    bin_files = sorted(DOWNLOADS_DIR.glob("*.bin"))

    if not bin_files:
        return '<li><span>No builds yet. Upload a sketch to generate one.</span></li>'

    items = []
    for file_path in bin_files:
        size_kb = round(file_path.stat().st_size / 1024, 1)
        name = file_path.stem
        items.append(
            f'<li><a href="downloads/{file_path.name}" target="_blank" rel="noreferrer">{file_path.name}</a><br><span>{name} · {size_kb} KB</span></li>'
        )
    return "\n".join(items)


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ino to Bin</title>
<style>
  :root {{
    --bg: #0b1220;
    --panel: #111b2d;
    --muted: #8ea3bd;
    --border: rgba(148, 163, 184, 0.2);
    --text: #edf2ff;
    --primary: #5ecbff;
    --primary-strong: #1fa7ff;
    --success: #5ce1a6;
    --danger: #ff7a7a;
  }}

  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: radial-gradient(circle at top, #12213d, var(--bg) 40%);
    color: var(--text);
    line-height: 1.5;
  }}
  .wrap {{
    max-width: 960px;
    margin: 0 auto;
    padding: 48px 20px 72px;
  }}
  .hero {{ margin-bottom: 28px; }}
  .eyebrow {{
    display: inline-block;
    color: var(--primary);
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 12px;
  }}
  h1 {{
    margin: 0 0 12px;
    font-size: clamp(2rem, 5vw, 3rem);
    line-height: 1.1;
  }}
  .subtitle {{
    color: var(--muted);
    max-width: 700px;
    font-size: 1rem;
  }}
  .grid {{
    display: grid;
    grid-template-columns: minmax(0, 1.2fr) minmax(260px, 0.8fr);
    gap: 24px;
  }}
  .panel {{
    background: rgba(17, 27, 45, 0.88);
    border: 1px solid var(--border);
    border-radius: 18px;
    box-shadow: 0 24px 48px rgba(15, 23, 42, 0.28);
    padding: 24px;
  }}
  label {{
    display: block;
    margin-bottom: 10px;
    color: var(--muted);
    font-size: 0.82rem;
    font-weight: 600;
    letter-spacing: 0.03em;
    text-transform: uppercase;
  }}
  input, select, button {{
    width: 100%;
    border-radius: 10px;
    border: 1px solid var(--border);
    background: rgba(15, 23, 42, 0.9);
    color: var(--text);
    padding: 12px 14px;
    font-size: 1rem;
  }}
  input:focus, select:focus {{
    outline: 2px solid rgba(94, 203, 255, 0.45);
    border-color: var(--primary);
  }}
  .field {{ margin-bottom: 18px; }}
  .upload-box {{
    border: 1px dashed rgba(94, 203, 255, 0.5);
    border-radius: 12px;
    padding: 18px;
    background: rgba(15, 23, 42, 0.5);
    text-align: center;
    color: var(--muted);
  }}
  .upload-box strong {{
    display: block;
    color: var(--text);
    margin-bottom: 6px;
  }}
  button {{
    border: none;
    background: linear-gradient(135deg, var(--primary), var(--primary-strong));
    color: #04111b;
    font-weight: 800;
    cursor: pointer;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
  }}
  button:hover {{
    transform: translateY(-1px);
    box-shadow: 0 10px 18px rgba(31, 167, 255, 0.35);
  }}
  button:disabled {{
    opacity: 0.6;
    cursor: not-allowed;
  }}
  .status {{
    min-height: 24px;
    margin-top: 18px;
    font-size: 0.95rem;
    color: var(--muted);
  }}
  .status.error {{ color: var(--danger); }}
  .status.success {{ color: var(--success); }}
  .meta {{
    margin-top: 24px;
    padding-top: 18px;
    border-top: 1px solid var(--border);
    color: var(--muted);
    font-size: 0.9rem;
  }}
  .meta a {{
    color: var(--primary);
    text-decoration: none;
  }}
  .meta a:hover {{ text-decoration: underline; }}
  .build-list {{
    margin-top: 12px;
    list-style: none;
    padding: 0;
  }}
  .build-list li {{
    border-bottom: 1px solid var(--border);
    padding: 12px 0;
  }}
  .build-list a {{
    color: var(--primary);
    text-decoration: none;
    font-weight: 600;
  }}
  .build-list span {{
    color: var(--muted);
    font-size: 0.9rem;
  }}
  @media (max-width: 760px) {{
    .grid {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>
  <div class="wrap">
    <div class="hero">
      <div class="eyebrow">Arduino firmware builder</div>
      <h1>Upload a sketch and build a .bin file</h1>
      <div class="subtitle">
        Pick an Arduino sketch, choose a board target, and trigger a GitHub Actions build that compiles it to a firmware binary for download.
      </div>
    </div>

    <div class="grid">
      <section class="panel">
        <form id="upload-form">
          <div class="field">
            <label for="repo-owner">GitHub repo owner</label>
            <input id="repo-owner" name="repo-owner" type="text" placeholder="your-github-user" required>
          </div>

          <div class="field">
            <label for="repo-name">GitHub repo name</label>
            <input id="repo-name" name="repo-name" type="text" placeholder="Ino-to-Bin" required>
          </div>

          <div class="field">
            <label for="github-token">GitHub personal access token</label>
            <input id="github-token" name="github-token" type="password" placeholder="ghp_..." required>
          </div>

          <div class="field">
            <label for="project-name">Project name</label>
            <input id="project-name" name="project-name" type="text" placeholder="My sketch" maxlength="64">
          </div>

          <div class="field">
            <label for="board">Board target</label>
            <select id="board" name="board">
              <option value="esp8266:esp8266:nodemcuv2">ESP8266 NodeMCU 1.0</option>
              <option value="esp8266:esp8266:generic">ESP8266 Generic</option>
              <option value="esp32:esp32:esp32">ESP32 Dev Module</option>
            </select>
          </div>

          <div class="field">
            <label for="sketch-file">Sketch file (.ino)</label>
            <div class="upload-box">
              <strong>Choose .ino file</strong>
              <input id="sketch-file" name="sketch-file" type="file" accept=".ino" required>
            </div>
          </div>

          <button id="submit-btn" type="submit">Build firmware</button>
          <div id="status" class="status" aria-live="polite"></div>
        </form>
      </section>

      <aside class="panel">
        <div class="eyebrow" style="margin-bottom: 8px;">Latest builds</div>
        <ul class="build-list" id="build-list">
          {download_list}
        </ul>
        <div class="meta">
          Need a token? Create a classic PAT with <strong>repo</strong> scope or a fine-grained token with workflow permission enabled for this repository.
          More details are in the repository README.
        </div>
      </aside>
    </div>
  </div>

  <script>
    const form = document.getElementById('upload-form');
    const statusEl = document.getElementById('status');
    const submitBtn = document.getElementById('submit-btn');
    const buildList = document.getElementById('build-list');

    function setStatus(message, kind = '') {{
      statusEl.textContent = message;
      statusEl.className = `status ${kind}`.trim();
    }}

    async function loadBuilds() {{
      const owner = document.getElementById('repo-owner').value.trim();
      const repo = document.getElementById('repo-name').value.trim();

      if (!owner || !repo) {{
        buildList.innerHTML = '<li><span>Enter repo details to see firmware builds.</span></li>';
        return;
      }}

      try {{
        const response = await fetch(`https://api.github.com/repos/${{owner}}/${{repo}}/contents/docs/downloads`, {{
          headers: {{ Accept: 'application/vnd.github+json' }}
        }});

        if (!response.ok) {{
          buildList.innerHTML = '<li><span>No builds found yet.</span></li>';
          return;
        }}

        const files = await response.json();
        const bins = Array.isArray(files) ? files.filter((item) => item.name.endsWith('.bin')) : [];

        if (!bins.length) {{
          buildList.innerHTML = '<li><span>No builds yet. Upload a sketch to generate one.</span></li>';
          return;
        }}

        buildList.innerHTML = bins
          .map((item) => {{
            const name = item.name.replace(/\\.bin$/i, '');
            return `<li><a href="https://github.com/${{owner}}/${{repo}}/raw/main/docs/downloads/${{encodeURIComponent(item.name)}}" target="_blank" rel="noreferrer">${{item.name}}</a><br><span>${{name}}</span></li>`;
          }})
          .join('');
      }} catch (error) {{
        buildList.innerHTML = '<li><span>No builds found yet.</span></li>';
      }}
    }}

    document.getElementById('repo-owner').addEventListener('input', loadBuilds);
    document.getElementById('repo-name').addEventListener('input', loadBuilds);

    form.addEventListener('submit', async (event) => {{
      event.preventDefault();
      const fileInput = document.getElementById('sketch-file');
      const file = fileInput.files[0];
      const owner = document.getElementById('repo-owner').value.trim();
      const repo = document.getElementById('repo-name').value.trim();
      const token = document.getElementById('github-token').value.trim();
      const projectName = document.getElementById('project-name').value.trim();
      const board = document.getElementById('board').value;

      if (!file) {{
        setStatus('Please choose a .ino file.', 'error');
        return;
      }}

      if (!file.name.toLowerCase().endsWith('.ino')) {{
        setStatus('Only .ino files are supported.', 'error');
        return;
      }}

      if (!owner || !repo || !token) {{
        setStatus('Repository owner, repo name, and GitHub token are required.', 'error');
        return;
      }}

      submitBtn.disabled = true;
      setStatus('Uploading sketch and queueing GitHub build…', '');

      try {{
        const text = await file.text();
        const encoded = btoa(unescape(encodeURIComponent(text)));
        const sketchName = file.name.replace(/\\.ino$/i, '');

        const response = await fetch(`https://api.github.com/repos/${{owner}}/${{repo}}/actions/workflows/build.yml/dispatches`, {{
          method: 'POST',
          headers: {{
            Authorization: `Bearer ${{token}}`,
            Accept: 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
            'Content-Type': 'application/json'
          }},
          body: JSON.stringify({{
            ref: 'main',
            inputs: {{
              project_name: projectName || sketchName,
              board,
              sketch_name: sketchName,
              sketch_content_b64: encoded
            }}
          }})
        }});

        if (response.status === 204) {{
          setStatus('Build queued successfully. GitHub Actions is compiling your firmware now.', 'success');
          loadBuilds();
        }} else {{
          const body = await response.text();
          throw new Error(body || 'Unknown GitHub API error');
        }}
      }} catch (error) {{
        console.error(error);
        setStatus('Request failed. Check the token, repo name, and workflow permissions, then try again.', 'error');
      }} finally {{
        submitBtn.disabled = false;
      }}
    }});

    loadBuilds();
  </script>
</body>
</html>
"""


def main() -> None:
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    html = PAGE_TEMPLATE.replace("{download_list}", build_download_list())
    OUTPUT_FILE.write_text(html)
    build_count = len(list(DOWNLOADS_DIR.glob("*.bin")))
    print(f"[generate_index] wrote {OUTPUT_FILE} with {build_count} build(s)")


if __name__ == "__main__":
    main()

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from flask import Flask, redirect, render_template_string, send_file, url_for

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

DATA_DIR = BASE_DIR / "data" / "violations" / "prototype_cases"
LOG_PATH = DATA_DIR / "violations.jsonl"
DASHBOARD_PATH = DATA_DIR / "dashboard.html"
VIDEO_PATH = DATA_DIR / "prototype_cases_video.mp4"

app = Flask(__name__)


HOME_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI Traffic Prototype</title>
  <style>
    body {
      margin: 0;
      font-family: "Segoe UI", Tahoma, sans-serif;
      background: linear-gradient(160deg, #07111e 0%, #0b1b31 55%, #081120 100%);
      color: #eef6ff;
    }
    .wrap {
      max-width: 960px;
      margin: 0 auto;
      padding: 40px 20px 56px;
    }
    .panel {
      background: rgba(10, 26, 47, 0.9);
      border: 1px solid rgba(134, 190, 255, 0.18);
      border-radius: 24px;
      padding: 28px;
      box-shadow: 0 18px 60px rgba(0, 0, 0, 0.25);
    }
    h1 {
      margin: 0 0 10px;
      font-size: 36px;
    }
    p {
      color: #a7bdd0;
      line-height: 1.6;
    }
    .actions {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      margin-top: 22px;
    }
    a, button {
      appearance: none;
      border: 0;
      border-radius: 14px;
      padding: 12px 18px;
      font-size: 15px;
      text-decoration: none;
      cursor: pointer;
    }
    .primary {
      background: #2fd27f;
      color: #041019;
      font-weight: 700;
    }
    .secondary {
      background: #13263d;
      color: #eef6ff;
      border: 1px solid rgba(134, 190, 255, 0.18);
    }
    .meta {
      margin-top: 20px;
      font-size: 14px;
      color: #a7bdd0;
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="panel">
      <h1>B.Tech AI Traffic Monitoring Prototype</h1>
      <p>
        This web app runs the overspeed prototype generator, serves the latest dashboard,
        and lets you open the generated demo video from one place for deployment or presentation.
      </p>
      <div class="actions">
        <a class="primary" href="{{ url_for('run_prototype') }}">Run Overspeed Prototype</a>
        <a class="secondary" href="{{ url_for('dashboard') }}">Open Dashboard</a>
        <a class="secondary" href="{{ url_for('video') }}">Open Video</a>
      </div>
      <div class="meta">
        Current outputs folder: <code>data/violations/prototype_cases</code>
      </div>
    </div>
  </div>
</body>
</html>"""


def load_records(path: Path) -> list[dict]:
    if not path.exists():
        return []
    records = []
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def build_html(records: list[dict]) -> str:
    overspeed = sum(1 for item in records if item.get("overspeed"))
    no_helmet = sum(1 for item in records if item.get("helmet_violation"))
    rows = []
    for item in records[-20:][::-1]:
        rows.append(
            f"""
            <tr>
              <td>{item.get('timestamp', '-')}</td>
              <td>{item.get('track_id', '-')}</td>
              <td>{item.get('plate_text', 'UNKNOWN')}</td>
              <td>{item.get('speed_kmph', '-')}</td>
              <td>{'Yes' if item.get('overspeed') else 'No'}</td>
              <td>{'Yes' if item.get('helmet_violation') else 'No'}</td>
              <td>{item.get('evidence_image', '-')}</td>
            </tr>
            """
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI Traffic Prototype Dashboard</title>
  <style>
    body {{
      margin: 0;
      font-family: "Segoe UI", Tahoma, sans-serif;
      background: linear-gradient(160deg, #07111e 0%, #0a1830 55%, #081120 100%);
      color: #edf6ff;
    }}
    .wrap {{
      max-width: 1100px;
      margin: 0 auto;
      padding: 32px 20px 48px;
    }}
    .panel {{
      padding: 24px 28px;
      border: 1px solid rgba(134, 190, 255, 0.18);
      border-radius: 24px;
      background: rgba(10, 26, 47, 0.88);
      box-shadow: 0 18px 60px rgba(0, 0, 0, 0.25);
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 18px;
      margin-top: 24px;
    }}
    .card {{
      padding: 20px;
      border-radius: 20px;
      border: 1px solid rgba(134, 190, 255, 0.18);
      background: rgba(10, 26, 47, 0.88);
    }}
    .label {{
      color: #9ab2c9;
      font-size: 14px;
      margin-bottom: 10px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}
    .value {{
      font-size: 34px;
      font-weight: 700;
    }}
    .table-panel {{
      margin-top: 24px;
      padding: 20px;
      border-radius: 20px;
      border: 1px solid rgba(134, 190, 255, 0.18);
      background: rgba(10, 26, 47, 0.88);
      overflow-x: auto;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }}
    th, td {{
      padding: 12px 10px;
      text-align: left;
      border-bottom: 1px solid rgba(255,255,255,0.08);
    }}
    th {{
      color: #9ab2c9;
      font-weight: 600;
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <section class="panel">
      <h1>B.Tech AI Traffic Monitoring Prototype</h1>
      <p>Recorded CCTV video is used for the project demo. The dashboard shows the latest overspeed prototype results.</p>
    </section>
    <section class="grid">
      <div class="card">
        <div class="label">Total Violations</div>
        <div class="value">{len(records)}</div>
      </div>
      <div class="card">
        <div class="label">Overspeed Cases</div>
        <div class="value">{overspeed}</div>
      </div>
      <div class="card">
        <div class="label">No Helmet Cases</div>
        <div class="value">{no_helmet}</div>
      </div>
    </section>
    <section class="table-panel">
      <h2>Recent Violation Log</h2>
      <table>
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Track ID</th>
            <th>Plate</th>
            <th>Speed</th>
            <th>Overspeed</th>
            <th>No Helmet</th>
            <th>Evidence</th>
          </tr>
        </thead>
        <tbody>
          {''.join(rows) or '<tr><td colspan="7">No violation records yet. Run the prototype first.</td></tr>'}
        </tbody>
      </table>
    </section>
  </div>
</body>
</html>"""


def generate_outputs() -> None:
    subprocess.run([sys.executable, "-m", "src.prototype_case_video"], cwd=BASE_DIR, check=True)
    subprocess.run(
        [
            sys.executable,
            "-m",
            "src.build_dashboard",
            "--input",
            str(LOG_PATH),
            "--output",
            str(DASHBOARD_PATH),
        ],
        cwd=BASE_DIR,
        check=True,
    )


@app.route("/")
def home():
    return render_template_string(HOME_HTML)


@app.route("/run")
def run_prototype():
    generate_outputs()
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    records = load_records(LOG_PATH)
    html = build_html(records)
    DASHBOARD_PATH.write_text(html, encoding="utf-8")
    return html


@app.route("/video")
def video():
    if not VIDEO_PATH.exists():
        generate_outputs()
    return send_file(VIDEO_PATH, mimetype="video/mp4")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

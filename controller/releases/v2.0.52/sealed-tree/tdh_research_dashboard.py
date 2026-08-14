#!/usr/bin/env python3
"""Read-only TDH Research Lab dashboard (stdlib, localhost only)."""
from __future__ import annotations

import csv
import html
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

ROOT = Path("/srv/tdh-collab/controller/strategy-lab-v2")


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def latest_run() -> Path | None:
    runs = [p for p in (ROOT / "runs").glob("tdh-strategy-lab-v2-*") if p.is_dir()]
    return max(runs, key=lambda p: p.stat().st_mtime_ns) if runs else None


def snapshot() -> dict[str, Any]:
    run = latest_run()
    supervisor = read_json(ROOT / "SUPERVISOR_STATE.json")
    state = read_json(run / "STATE.json") if run else {}
    synthesis_paths = sorted(run.glob("round-*/DUAL_AGENT_SYNTHESIS.json")) if run else []
    synthesis = read_json(synthesis_paths[-1]) if synthesis_paths else {}
    trials = 0
    performance = 0
    if run and (run / "TRIALS.jsonl").is_file():
        for line in (run / "TRIALS.jsonl").read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                row = json.loads(line)
            except Exception:
                continue
            trials += 1
            performance += int(row.get("classification") == "PERFORMANCE")
    return {
        "service": "TDH Research Lab",
        "run_id": run.name if run else None,
        "controller_stage": state.get("stage", "UNKNOWN"),
        "research_round": state.get("research_round", 0),
        "supervisor_status": supervisor.get("status", "UNKNOWN"),
        "completed_epochs": supervisor.get("completed_epoch_count", 0),
        "codex_tokens": supervisor.get("cumulative_codex_tokens", 0),
        "claude_tokens": supervisor.get("cumulative_claude_tokens", 0),
        "no_progress_streak": supervisor.get("no_progress_run_streak", 0),
        "trials": trials,
        "performance_trials": performance,
        "dual_synthesis": synthesis,
        "offline": True,
        "trading_actions": False,
        "exchange_api_access": False,
    }


def page(data: dict[str, Any]) -> bytes:
    cards = "".join(
        f"<section><small>{html.escape(label)}</small><strong>{html.escape(str(value))}</strong></section>"
        for label, value in (
            ("Supervisor", data["supervisor_status"]), ("Controller", data["controller_stage"]),
            ("Epochs", data["completed_epochs"]), ("Round", data["research_round"]),
            ("Backtests", data["trials"]), ("Performance", data["performance_trials"]),
            ("Codex tokens", data["codex_tokens"]), ("Claude tokens", data["claude_tokens"]),
        )
    )
    synth = html.escape(json.dumps(data["dual_synthesis"], indent=2, ensure_ascii=False))
    return f"""<!doctype html><html><head><meta charset=utf-8><meta http-equiv=refresh content=15>
<title>TDH Research Lab</title><style>
body{{font-family:system-ui;background:#07111f;color:#e8f0ff;margin:0;padding:28px}}
h1{{margin:0}} .sub{{color:#8fa6c9;margin:6px 0 24px}} main{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}}
section,article{{background:#0e1c30;border:1px solid #213653;border-radius:14px;padding:16px}}
small{{display:block;color:#8fa6c9}} strong{{display:block;font-size:22px;margin-top:5px}} article{{margin-top:16px}} pre{{white-space:pre-wrap}}
.ok{{color:#62e6a7}} @media(max-width:800px){{main{{grid-template-columns:repeat(2,1fr)}}}}
</style></head><body><h1>TDH Research Lab</h1><div class=sub>Dual-agent offline backtest system · <span class=ok>Trading disabled</span></div>
<main>{cards}</main><article><small>Active run</small><strong>{html.escape(str(data['run_id']))}</strong></article>
<article><small>Latest Codex–Claude synthesis</small><pre>{synth}</pre></article></body></html>""".encode()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        data = snapshot()
        if self.path == "/api/status":
            body = json.dumps(data, ensure_ascii=False, indent=2).encode()
            kind = "application/json; charset=utf-8"
        elif self.path in {"/", "/index.html"}:
            body = page(data)
            kind = "text/html; charset=utf-8"
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_: Any) -> None:
        return


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 8765), Handler).serve_forever()

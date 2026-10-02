"""``amr-report`` — a status dashboard generated from the official APIs.

Collects everything from documented endpoints only — robot: ``/status``,
``/missions``, ``/mission_queue``, ``/log/error_reports``,
``/statistics/distance``; fleet: ``/robots``, ``/robots/{id}``, ``/order`` —
and renders a self-contained HTML dashboard: a shift-level KPI row,
current-status indicators, the daily trend, and a collapsed event log. Works against real
robots and the emulator alike; nothing here touches ``/_emulator`` surfaces.

    amr-report http://192.168.12.20 -o robot.html
    amr-report http://127.0.0.1:8090 --api-key <key> -o fleet.html --json

From Python: ``collect_report()`` / ``render_report()`` / ``write_report()``
(async twins where it matters). Pass ``session_id=`` to report on an
emulator session's isolated robot.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from html import escape
from pathlib import Path
from typing import Any

import httpx

from amr_client.auth import DEFAULT_PASSWORD, DEFAULT_USERNAME, robot_token
from amr_client.discovery import detect_server_async

ROBOT_BASE = "/api/v2.0.0"
FLEET_BASE = "/api/v1"
DEFAULT_API_KEY = "distributor"


def _unsupported_kind_message(kind: str) -> str:
    return f"cannot report on a {kind!r} target; point amr-report at a robot or fleet"


async def _get_json(http: httpx.AsyncClient, path: str) -> Any:
    response = await http.get(path)
    response.raise_for_status()
    return response.json()


def _as_list(value: Any) -> list:
    """MiR specs declare some list endpoints with the element's object schema,
    and servers differ on which shape they answer with — accept both."""
    if isinstance(value, list):
        return value
    return [value] if isinstance(value, dict) else []


def _entry_minutes(started: str | None, finished: str | None) -> int | None:
    if not started or not finished:
        return None
    from datetime import datetime

    fmt = "%Y-%m-%dT%H:%M:%S"
    delta = datetime.strptime(finished, fmt) - datetime.strptime(started, fmt)
    return round(delta.total_seconds() / 60)


async def _collect_robot(
    base: str, version: str | None, headers: dict, timeout: float, httpx_kwargs: dict
) -> dict:
    async with httpx.AsyncClient(
        base_url=base, headers=headers, timeout=timeout, **httpx_kwargs
    ) as http:
        status = await _get_json(http, f"{ROBOT_BASE}/status")
        mission_names = {
            m["guid"]: m["name"] for m in _as_list(await _get_json(http, f"{ROBOT_BASE}/missions"))
        }
        queue: list[dict] = []
        for item in _as_list(await _get_json(http, f"{ROBOT_BASE}/mission_queue")):
            queue.append(await _get_json(http, f"{ROBOT_BASE}/mission_queue/{item['id']}"))
        error_reports = await _get_json(http, f"{ROBOT_BASE}/log/error_reports")
        distance = await _get_json(http, f"{ROBOT_BASE}/statistics/distance")

    robot = {
        "name": status.get("robot_name"),
        "model": status.get("robot_model"),
        "state": status.get("state_text"),
        "battery": round(float(status.get("battery_percentage", 0.0)), 1),
        "mission_text": status.get("mission_text"),
        "position": status.get("position", {}),
        # code 0 entries are schema placeholders, not live errors
        "errors": [e for e in status.get("errors", []) if e.get("code")],
        "uptime_s": status.get("uptime"),
    }

    timeline = []
    for entry in queue:
        name = mission_names.get(entry.get("mission_id", ""), entry.get("mission_id", "?"))
        state = entry.get("state", "?")
        when = entry.get("finished") or entry.get("started") or entry.get("ordered")
        minutes = _entry_minutes(entry.get("started"), entry.get("finished"))
        text = f"Mission '{name}' — {state}" + (f" ({minutes} min)" if minutes is not None else "")
        timeline.append({"time": when or "", "kind": "mission", "state": state, "text": text})
    for report in _as_list(error_reports):
        module = report.get("module", "?")
        description = report.get("description", "")
        if module == "emulated" and description == "emulated":
            continue  # seeded placeholder, not an event
        timeline.append(
            {
                "time": report.get("time", ""),
                "kind": "error",
                "state": "Error",
                "text": f"{module}: {description}",
            }
        )
    timeline.sort(key=lambda e: e["time"])

    return {
        "kind": "robot",
        "target": base,
        "version": version,
        "robots": [robot],
        "trend_label": "distance driven (m)",
        "trend": [
            {"date": str(d.get("date", ""))[:10], "value": d.get("distance", 0.0)}
            for d in _as_list(distance)
        ],
        "timeline": timeline,
    }


async def _collect_fleet(
    base: str, version: str | None, headers: dict, timeout: float, httpx_kwargs: dict
) -> dict:
    async with httpx.AsyncClient(
        base_url=base, headers=headers, timeout=timeout, **httpx_kwargs
    ) as http:
        listing = await _get_json(http, f"{FLEET_BASE}/robots")
        robots = []
        for identity in listing.get("robots", []):
            detail = await _get_json(http, f"{FLEET_BASE}/robots/{identity['robot-id']}")
            runtime = detail.get("runtime-data", {})
            robots.append(
                {
                    "name": identity.get("name"),
                    "model": identity.get("model"),
                    "state": None,  # the Fleet API reports runtime data, not a scalar state
                    "battery": round(float(runtime.get("battery-percentage", 0.0)), 1),
                    "mission_text": None,
                    "position": runtime.get("pose", {}),
                    "errors": [],
                    "uptime_s": None,
                }
            )
        orders = await _get_json(http, f"{FLEET_BASE}/order")

    timeline = []
    per_day: dict[str, int] = {}
    for order in _as_list(orders):
        when = order.get("order-queued") or order.get("order-created") or ""
        per_day[when[:10]] = per_day.get(when[:10], 0) + 1
        timeline.append(
            {
                "time": when,
                "kind": "order",
                "state": order.get("order-status", "?"),
                "text": (
                    f"Order {order.get('order-id', '?')[:13]}… — "
                    f"mission '{order.get('mission-name', '?')}' on "
                    f"{order.get('robot-name', 'unassigned')} · {order.get('order-status', '?')}"
                ),
            }
        )
    timeline.sort(key=lambda e: e["time"])

    return {
        "kind": "fleet",
        "target": base,
        "version": version,
        "robots": robots,
        "trend_label": "orders per day",
        "trend": [{"date": day, "value": n} for day, n in sorted(per_day.items())],
        "timeline": timeline,
    }


async def collect_report_async(
    base_url: str,
    *,
    username: str = DEFAULT_USERNAME,
    password: str = DEFAULT_PASSWORD,
    api_key: str = DEFAULT_API_KEY,
    session_id: str | None = None,
    timeout: float = 10.0,
    **httpx_kwargs: Any,
) -> dict:
    """Report data for the robot or fleet at *base_url*, official endpoints only."""
    base = base_url.rstrip("/")
    info = await detect_server_async(base, api_key=api_key, timeout=timeout, **httpx_kwargs)
    session = {"X-AMR-Session": session_id} if session_id else {}
    if info.kind == "robot":
        headers = {"Authorization": f"Basic {robot_token(username, password)}", **session}
        return await _collect_robot(base, info.version, headers, timeout, httpx_kwargs)
    if info.kind == "fleet":
        headers = {"x-api-key": api_key, **session}
        return await _collect_fleet(base, info.version, headers, timeout, httpx_kwargs)
    raise ValueError(_unsupported_kind_message(info.kind))


def collect_report(base_url: str, **kwargs: Any) -> dict:
    """Sync twin of :func:`collect_report_async`."""
    return asyncio.run(collect_report_async(base_url, **kwargs))


# --- rendering -----------------------------------------------------------------
# Same brand system as the project's docs pages, self-contained (no external
# fonts or scripts) so the file works offline and in restricted viewers.

_STATE_LED = {
    "Ready": "#1d9e61",
    "Executing": "#1a76bc",
    "Pause": "#c77700",
    "Manualcontrol": "#c77700",
    "EmergencyStop": "#cf3228",
    "Error": "#cf3228",
}

_CSS = """
:root { --brand:#00bfff; --blue:#4da3e8; --blue-deep:#7cc4f4; --ink:#e8eaf2;
  --ink-dim:#a6abc4; --ink-faint:#767c99; --tint:#1a2233; --tint-2:#24304a;
  --line:#262a40; --bg:#0d0f1c; --panel:#151829;
  --green:#2ecc7a; --amber:#e6a23c; --red:#ff6b5e;
  --mono:ui-monospace,SFMono-Regular,Menlo,monospace;
  --sans:-apple-system,"Segoe UI",Helvetica,Arial,sans-serif; }
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:17px;line-height:1.6}
.brandbar{height:4px;background:var(--brand)}
.wrap{max-width:1140px;margin:0 auto;padding:22px 24px 70px}
h1{font-size:34px;font-weight:300}
h1 span{color:var(--brand)}
.sub{font-size:16px;color:var(--ink-dim);margin-bottom:22px}
code{font-family:var(--mono);font-size:.92em;background:var(--tint);
  border:1px solid var(--tint-2);border-radius:4px;padding:0 4px;color:var(--blue-deep)}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:.4rem;
  box-shadow:0 1px 3px rgba(0,0,0,.35);padding:18px 22px}
.kpi .lb{font-size:15px;color:var(--ink-dim)}
.kpi .v{font-size:46px;font-weight:600;line-height:1.2;letter-spacing:-.5px}
.kpi .v small{font-size:24px;font-weight:400;color:var(--ink-dim)}
.kpi .d{font-size:14px;color:var(--ink-faint)}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:.4rem;
  box-shadow:0 1px 3px rgba(0,0,0,.35);margin-top:18px;overflow:hidden}
.panel-head{display:flex;align-items:center;gap:12px;padding:14px 20px;
  border-bottom:1px solid var(--line);font-size:19px;font-weight:600}
.panel-head::before{content:"";width:9px;height:9px;border-radius:2px;background:var(--brand)}
.panel-head .tag{margin-left:auto;color:var(--ink-faint);font-size:12.5px;
  font-family:var(--mono);font-weight:400}
.panel-body{padding:20px}
.bots{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:16px}
.bot{border:1px solid var(--line);border-radius:.4rem;padding:16px 18px}
.bot .nm{font-weight:600;font-size:19px;display:flex;align-items:center;gap:10px}
.led{width:12px;height:12px;border-radius:50%;flex:none}
.bot .st{font-size:15px;color:var(--ink-dim)}
.batt{margin-top:10px;height:10px;border-radius:5px;background:var(--tint);
  border:1px solid var(--tint-2);overflow:hidden}
.batt i{display:block;height:100%;background:var(--green)}
.batt.low i{background:var(--red)}
.kv{margin-top:10px;font-size:15px;color:var(--ink-dim);display:grid;gap:2px;font-variant-numeric:tabular-nums}
.err{color:var(--red);font-size:15px;margin-top:8px}
.trend svg{display:block;width:100%;height:auto}
details.panel>summary{cursor:pointer;list-style:none}
details.panel>summary::-webkit-details-marker{display:none}
details.panel>summary .tag::after{content:" · click to expand"}
details.panel[open]>summary .tag::after{content:" · click to collapse"}
.tl{max-height:480px;overflow-y:auto}
.ev{display:flex;gap:12px;padding:7px 8px;border-radius:6px;font-size:15px}
.ev:hover{background:var(--tint)}
.ev .t{color:var(--ink-faint);font-family:var(--mono);font-size:13px;flex:0 0 152px}
.ev.error .tx{color:var(--red)}
.ev .tx{color:var(--ink-dim)}
footer{color:var(--ink-faint);font-size:14px;margin-top:20px}
"""


def _kpi_tiles(data: dict) -> list[tuple[str, str, str]]:
    """Shift-level headline numbers, computed from the collected data."""
    robots = data.get("robots", [])
    timeline = data.get("timeline", [])
    trend = data.get("trend", [])
    today = round(trend[-1]["value"]) if trend else 0
    if data.get("kind") == "fleet":
        orders = [e for e in timeline if e["kind"] == "order"]
        done = sum(1 for e in orders if e.get("state") == "Done")
        batteries = [r.get("battery", 0.0) for r in robots]
        average = round(sum(batteries) / len(batteries)) if batteries else 0
        return [
            ("Robots on the floor", f"{len(robots)}", ""),
            ("Orders this shift", f"{len(orders)}", f"{done} completed"),
            ("Orders today", f"{today:,}", ""),
            ("Fleet battery", f"{average}<small>%</small>", "average across robots"),
        ]
    robot = robots[0] if robots else {}
    missions = [e for e in timeline if e["kind"] == "mission"]
    done = sum(1 for e in missions if e.get("state") == "Done")
    faults = sum(1 for e in timeline if e["kind"] == "error")
    active = len(robot.get("errors", []))
    state = robot.get("state") or "—"
    uptime_s = robot.get("uptime_s")
    up = f" · up {uptime_s / 3600:.1f} h" if uptime_s else ""
    return [
        ("Missions this shift", f"{len(missions)}", f"{done} completed"),
        ("Distance today", f"{today:,}<small> m</small>", ""),
        ("Battery", f"{robot.get('battery', 0)}<small>%</small>", f"{escape(state)}{up}"),
        ("Faults this shift", f"{faults}", f"{active} active now"),
    ]


def _render_kpis(data: dict) -> str:
    tiles = "".join(
        f'<div class="kpi"><div class="lb">{escape(label)}</div>'
        f'<div class="v">{value}</div>' + (f'<div class="d">{sub}</div>' if sub else "") + "</div>"
        for label, value, sub in _kpi_tiles(data)
    )
    return f'<div class="kpis">{tiles}</div>'


def _render_bot(robot: dict) -> str:
    led = _STATE_LED.get(robot.get("state") or "", "#8a8fa5")
    battery = robot.get("battery", 0.0)
    low = " low" if battery < 20 else ""
    position = robot.get("position") or {}
    pos = f"({position.get('x', '?')}, {position.get('y', '?')})" if position else "—"
    state = robot.get("state") or "—"
    mission = robot.get("mission_text") or "—"
    errors = "".join(
        f'<div class="err">&#9888; {escape(str(e.get("module", "?")))}: '
        f"{escape(str(e.get('description', '')))}</div>"
        for e in robot.get("errors", [])
    )
    return f"""<div class="bot">
  <div class="nm"><span class="led" style="background:{led}"></span>{
        escape(str(robot.get("name", "?")))
    }
    <span style="color:var(--ink-faint);font-weight:400;font-size:11px">{
        escape(str(robot.get("model", "")))
    }</span></div>
  <div class="st">{escape(state)} &middot; {escape(str(mission))}</div>
  <div class="batt{low}"><i style="width:{max(0.0, min(100.0, battery))}%"></i></div>
  <div class="kv"><div>battery {battery}%</div><div>position {escape(pos)}</div></div>
  {errors}
</div>"""


def _render_trend(trend: list[dict], label: str) -> str:
    if not trend:
        return '<p style="color:var(--ink-faint)">no data yet</p>'
    width, height, pad = 720, 160, 28
    bar_zone = width - 2 * pad
    peak = max((d["value"] for d in trend), default=0) or 1
    step = bar_zone / len(trend)
    bar_w = min(16.0, step - 8)
    bars = []
    for i, day in enumerate(trend):
        h = (day["value"] / peak) * (height - 2 * pad)
        bx = pad + i * step + (step - bar_w) / 2
        by = height - pad - h
        bars.append(
            f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bar_w:.1f}" height="{max(h, 1):.1f}" '
            f'rx="4" fill="#1a76bc"><title>{escape(day["date"])}: {day["value"]}</title></rect>'
            f'<text x="{bx + bar_w / 2:.1f}" y="{height - pad + 16}" text-anchor="middle" '
            f'font-size="12" fill="#767c99">{escape(day["date"][5:])}</text>'
            f'<text x="{bx + bar_w / 2:.1f}" y="{by - 6:.1f}" text-anchor="middle" '
            f'font-size="12" fill="#a6abc4">{round(day["value"])}</text>'
        )
    baseline = (
        f'<line x1="{pad}" y1="{height - pad}" x2="{width - pad}" y2="{height - pad}" '
        f'stroke="#3a4059" stroke-width="1"/>'
    )
    return (
        f'<div class="trend"><svg viewBox="0 0 {width} {height}" role="img" '
        f'aria-label="{escape(label)}">{baseline}{"".join(bars)}</svg></div>'
    )


def render_report(data: dict) -> str:
    """Self-contained HTML dashboard for a collected report."""
    kind = data.get("kind", "robot")
    robots = data.get("robots", [])
    timeline = data.get("timeline", [])
    icon = {"mission": "&#10003;", "order": "&#9654;", "error": "&#9888;"}
    rows = "".join(
        f'<div class="ev {e["kind"]}"><span class="t">{escape(e["time"].replace("T", " "))}</span>'
        f"<span>{icon.get(e['kind'], '&middot;')}</span>"
        f'<span class="tx">{escape(e["text"])}</span></div>'
        for e in timeline
    )
    title = "Fleet report" if kind == "fleet" else "Robot report"
    version = data.get("version") or "unknown version"
    status_src = "GET /robots + /robots/{id}" if kind == "fleet" else "GET /status"
    trend_src = "GET /order" if kind == "fleet" else "GET /statistics/distance"
    trend_svg = _render_trend(data.get("trend", []), data.get("trend_label", ""))
    timeline_src = "GET /order" if kind == "fleet" else "GET /mission_queue + /log/error_reports"
    timeline_rows = rows or '<p style="color:var(--ink-faint)">nothing yet</p>'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — {escape(str(data.get("target", "")))}</title>
<style>{_CSS}</style>
</head>
<body>
<div class="brandbar"></div>
<div class="wrap">
  <h1>{title} <span>{escape(str(version))}</span></h1>
  <div class="sub">{escape(str(data.get("target", "")))} &middot;
  generated from official API endpoints</div>

  {_render_kpis(data)}

  <div class="panel">
    <div class="panel-head">Current status <span class="tag">{status_src}</span></div>
    <div class="panel-body"><div class="bots">{"".join(_render_bot(r) for r in robots)}</div></div>
  </div>

  <div class="panel">
    <div class="panel-head">Daily trend — {escape(data.get("trend_label", ""))}
      <span class="tag">{trend_src}</span></div>
    <div class="panel-body">{trend_svg}</div>
  </div>

  <details class="panel">
    <summary class="panel-head">Event log
      <span class="tag">{len(timeline)} events · {timeline_src}</span></summary>
    <div class="panel-body"><div class="tl">{timeline_rows}</div></div>
  </details>

  <footer>Generated by <code>amr-report</code> (amr-client) from documented endpoints only —
  works identically against real MiR robots, fleets, and the emulator.</footer>
</div>
</body>
</html>
"""


def write_report(base_url: str, path: str | Path, **kwargs: Any) -> Path:
    """Collect and render in one step; returns the written path."""
    out = Path(path)
    out.write_text(render_report(collect_report(base_url, **kwargs)))
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="amr-report",
        description="Generate a status/trend/timeline dashboard from a MiR robot or fleet.",
    )
    parser.add_argument("target", help="base URL of the robot or fleet (e.g. http://192.168.12.20)")
    parser.add_argument("-o", "--output", default="amr-report.html", help="HTML output path")
    parser.add_argument("--username", default=DEFAULT_USERNAME, help="robot API username")
    parser.add_argument("--password", default=DEFAULT_PASSWORD, help="robot API password")
    parser.add_argument("--api-key", default=DEFAULT_API_KEY, help="fleet x-api-key")
    parser.add_argument("--session", default=None, help="X-AMR-Session id (emulator)")
    parser.add_argument("--json", action="store_true", help="print collected data as JSON too")
    args = parser.parse_args(argv)

    data = collect_report(
        args.target,
        username=args.username,
        password=args.password,
        api_key=args.api_key,
        session_id=args.session,
    )
    out = Path(args.output)
    out.write_text(render_report(data))
    if args.json:
        print(json.dumps(data, indent=1))
    robots = ", ".join(f"{r['name']} {r['battery']}%" for r in data["robots"])
    print(f"amr-report: {data['kind']} {data.get('version')} -> {out} ({robots})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

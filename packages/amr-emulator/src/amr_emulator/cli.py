"""Run the emulator: ``amr-emulator --mir-version 3.5.4 --port 8080``."""

from __future__ import annotations

import argparse
import os

from amr_emulator import auth, registry
from amr_emulator._version import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="amr-emulator",
        description="Local emulator for the MiR robot REST API (/api/v2.0.0).",
    )
    parser.add_argument(
        "--mir-version",
        default=None,
        help=f"MiR software version to emulate; one of {registry.supported_versions()}",
    )
    parser.add_argument(
        "--fleet-version",
        default=None,
        metavar="VERSION",
        help=(
            "Emulate MiR Fleet Enterprise instead of a single robot; one of "
            f"{registry.fleet_supported_versions()} (the fleet embeds robot emulators "
            "and controls them over their own REST API)"
        ),
    )
    parser.add_argument(
        "--fleet-robots",
        default=None,
        metavar="V1,V2,...",
        help=(
            "Robot software versions the fleet manages, comma-separated "
            "(default: two robots on the newest tracked version)"
        ),
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("AMR_EMULATOR_API_KEY", "distributor"),
        help="Accepted x-api-key for the fleet API (env: AMR_EMULATOR_API_KEY)",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument(
        "--no-auth", action="store_true", help="Disable Authorization header checks"
    )
    parser.add_argument(
        "--cors", action="store_true", help="Allow cross-origin requests (browser dashboards)"
    )
    parser.add_argument(
        "--latency-ms",
        type=float,
        default=0.0,
        help="Baseline response delay in milliseconds (per-request X-AMR-Latency overrides)",
    )
    parser.add_argument(
        "--mission-duration",
        type=float,
        default=10.0,
        help="Seconds a queued mission spends Executing before it is Done (default: 10)",
    )
    parser.add_argument(
        "--time-scale",
        type=float,
        default=1.0,
        metavar="N",
        help=(
            "Run simulated time Nx faster than wall time; missions and battery "
            "curves keep realistic simulated durations and timestamps "
            "(runtime control: PUT /_emulator/clock)"
        ),
    )
    parser.add_argument(
        "--replay",
        default=None,
        metavar="SCENARIO.json",
        help=(
            "Replay a scenario recorded via /_emulator/recorder against a fresh "
            "emulator and exit non-zero on any mismatch"
        ),
    )
    parser.add_argument(
        "--export",
        choices=("swagger2", "openapi3"),
        default=None,
        help="Print the selected version's API definition to stdout and exit",
    )
    parser.add_argument(
        "--username",
        default=os.environ.get("AMR_EMULATOR_USERNAME", auth.DEFAULT_USERNAME),
        help="Accepted username (env: AMR_EMULATOR_USERNAME)",
    )
    parser.add_argument(
        "--password",
        default=os.environ.get("AMR_EMULATOR_PASSWORD", auth.DEFAULT_PASSWORD),
        help="Accepted password, pre-hash (env: AMR_EMULATOR_PASSWORD)",
    )
    parser.add_argument("--version", action="version", version=f"amr-emulator {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.replay:
        import json

        from amr_emulator.record import replay

        with open(args.replay) as fh:
            scenario = json.load(fh)
        problems = replay(scenario)
        label = f"{scenario.get('family', 'robot')} {scenario.get('version', '?')}"
        if problems:
            for problem in problems:
                print(problem)
            print(f"replay: {len(problems)} mismatches against {label}")
            return 1
        print(f"replay: {len(scenario.get('steps', []))} steps reproduced exactly ({label})")
        return 0

    if args.export:
        import json

        from amr_emulator.spec import load_spec

        version, path = registry.spec_path(args.mir_version)
        doc = load_spec(path, version).document
        if args.export == "openapi3" and doc.get("swagger") == "2.0":
            from amr_emulator.openapi3 import to_openapi3

            doc = to_openapi3(doc)
        try:
            print(json.dumps(doc, indent=1))
        except BrokenPipeError:  # e.g. piped into `head` — not an error
            import os
            import sys

            devnull_fd = os.open(os.devnull, os.O_WRONLY)
            try:
                os.dup2(devnull_fd, sys.stdout.fileno())
            finally:
                os.close(devnull_fd)
        return 0

    import uvicorn

    if args.time_scale != 1.0:
        from amr_emulator import behaviors

        problem = behaviors.set_time_scale({"scale": args.time_scale})
        if problem is not None:
            parser.error(problem)
        print(f"time scale: {args.time_scale}x (simulated seconds per wall second)")

    if args.fleet_version:
        from amr_emulator.fleet import create_fleet_app

        robot_versions = (
            tuple(v.strip() for v in args.fleet_robots.split(",") if v.strip())
            if args.fleet_robots
            else None
        )
        app = create_fleet_app(
            args.fleet_version,
            robot_versions=robot_versions,
            api_key=args.api_key,
            enforce_auth=not args.no_auth,
            robot_username=args.username,
            robot_password=args.password,
            cors=args.cors,
            mission_duration=args.mission_duration,
        )
        version = app.state.fleet_version
        robots = ", ".join(r.mir_version for r in app.state.emulator.robots)
        print(
            f"amr-emulator: MiR Fleet {version} Integration API on "
            f"http://{args.host}:{args.port}/api/v1 (robots: {robots})"
        )
        if not args.no_auth:
            print("auth: x-api-key header — default key 'distributor'")
        uvicorn.run(app, host=args.host, port=args.port, log_level="warning")
        return 0

    from amr_emulator.app import create_app

    app = create_app(
        args.mir_version,
        enforce_auth=not args.no_auth,
        username=args.username,
        password=args.password,
        cors=args.cors,
        mission_duration=args.mission_duration,
        latency_ms=args.latency_ms,
    )
    version = app.state.mir_version
    print(f"amr-emulator: MiR {version} REST API on http://{args.host}:{args.port}/api/v2.0.0")
    if not args.no_auth:
        print(
            "auth: Authorization: Basic BASE64(<user>:SHA-256(<password>)) — "
            f"default account {auth.DEFAULT_USERNAME!r}"
        )
    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

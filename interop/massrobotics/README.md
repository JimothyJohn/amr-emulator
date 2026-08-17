# External conformance: official MassRobotics reference receiver

`packages/massrobotics-emulator`'s own sender↔receiver tests share this
repo's schema handling — consistent, but circular. This harness closes the
loop against the standard's own reference implementation: the Node/Ajv
receiver from [MassRobotics-AMR/AMR_Interop_Standard](https://github.com/MassRobotics-AMR/AMR_Interop_Standard),
built **unmodified** at the commit pinned in the `Dockerfile` (the same
commit the vendored schema's `registry.json` records).

The run starts all four Vecna-model robots (APT, ATG, AFL, CPJ) against
the containerized receiver and witnesses its verdicts over the `/ui`
WebSocket, where the receiver broadcasts `{message, isValid, errors}` for
every message it validates.

## Run it

```sh
uv run interop/massrobotics/run_interop.py        # builds the image first time
uv run interop/massrobotics/run_interop.py --skip-build
```

Requires Docker. Exit 0 = every identityReport and statusReport we sent —
idle, navigating (path/destinations), erroring, charging — was judged
valid by the official Ajv validator, **and** a deliberately-invalid probe
message was judged invalid (proving the witness channel actually detects
bad traffic rather than rubber-stamping).

# amr-emulator

Local emulator of the Mobile Industrial Robots (MiR) robot REST API
(`/api/v2.0.0`), driven by the official API definition files. Develop and test
MiR integrations without a robot.

```sh
# from a checkout of https://github.com/JimothyJohn/amr-emulator
uv run amr-emulator --mir-version 3.5.4 --port 8080
curl -H "Authorization: Basic $(printf '%s:%s' distributor "$(printf distributor | shasum -a 256 | cut -d' ' -f1)" | base64)" \
  http://127.0.0.1:8080/api/v2.0.0/status
```

- Every endpoint in the bundled spec is served; responses conform to the
  spec's response schemas.
- Stateful behavior for the important endpoints: `/status`, `/mission_queue`,
  `/registers`, plus generic CRUD everywhere else.
- MiR-style auth (`Basic BASE64(user:SHA-256(password))`, default
  `distributor`/`distributor`), or `--no-auth`.
- The package version matches the MiR software version it emulates by default;
  other bundled versions are selectable with `--mir-version` or
  `create_app("2.7.0")`.

See the repository root README for how versions are tracked and updated.

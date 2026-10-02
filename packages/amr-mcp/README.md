# amr-mcp

MCP (Model Context Protocol) server that lets any MCP client — Claude Code,
Claude Desktop, or anything else speaking MCP — control MiR robots and
fleets in natural language. It wraps the documented MiR REST APIs (robot
`/api/v2.0.0`, fleet `/api/v1`), so it works identically against this
repo's emulator and against real hardware.

## Tools

Discovery: `amr_discover_robots` — find robots on the network by IP when you
don't know an address: sweeps candidate hosts (a CIDR, host list, or the
local /24 by default) on ports 80/8080 and returns every confirmed MiR
target with its kind and software version. Then set `AMR_ROBOT_URL` /
`AMR_FLEET_URL` to a found URL.

`amr_server_info` — identifies what the configured URLs point at
(robot, fleet, or the multi-version demo dispatcher) and which MiR software
version each target reports. The other tools run the same handshake on
their first call, so pointing `AMR_ROBOT_URL` at a dispatcher root just
works: the newest served version is used unless `AMR_VERSION` /
`AMR_FLEET_VERSION` pins one. No version needs to be installed or
configured to match the target.

Robot: `amr_robot_status`, `amr_set_robot_state` (ready/pause/manual),
`amr_clear_error`, `amr_list_missions`, `amr_queue_mission` (by name or
guid, optional wait-for-completion), `amr_mission_queue`,
`amr_cancel_missions`, `amr_wait_for` (server-side wait on a condition —
queue idle, state, errors cleared, battery threshold — with progress
notifications), `amr_read_register`, `amr_write_register`,
`amr_manage_faults` (emulator-only fault injection).

## MCP 2.0 agent interface

Built on MCP SDK 2.0 (`MCPServer`), the server is more than a bag of
tools:

- **Structured output.** Every tool advertises an output schema and
  returns structured content — agents read fields, not prose. Failures
  use the `isError` channel (`ToolError`) with the fix spelled out in the
  message.
- **Elicitation** (when the client supports it): clearing the whole
  mission queue asks for confirmation first, and an ambiguous mission
  name asks which mission was meant (an enum of the matching guids)
  instead of erroring. Clients without elicitation keep the plain
  behavior.
- **Server-side waits.** `amr_wait_for` replaces agent-side polling
  loops: one call that polls the robot, streams progress notifications,
  and returns the observed state transitions plus the final status.
- **Live status resource.** `mir://robot/status` serves the trimmed
  status document; `amr_wait_for` announces resource updates on every
  observed state change.
- **Instructions & caching.** The server ships initialize-time
  instructions (workflow, guardrails) and marks its static tool/resource
  lists cacheable.

Fleet: `amr_fleet_robots`, `amr_fleet_dispatch` (serial orders by mission
name), `amr_fleet_order_status` (check/abort).

## Configuration (environment)

| Variable | Default | Meaning |
|---|---|---|
| `AMR_ROBOT_URL` | `http://127.0.0.1:8080` | Robot base URL |
| `AMR_FLEET_URL` | = `AMR_ROBOT_URL` | Fleet base URL |
| `AMR_USERNAME` / `AMR_PASSWORD` | `distributor` | Robot account (password pre-hash) |
| `AMR_API_KEY` | `distributor` | Fleet `x-api-key` |
| `AMR_SESSION` | unset | Emulator-only `X-AMR-Session` isolation id |
| `AMR_VERSION` | newest served | Robot version to pin when the URL is a multi-version dispatcher |
| `AMR_FLEET_VERSION` | newest served | Fleet version to pin, same case |

## Use with Claude Code

```sh
# terminal 1: something to control
uv run amr-emulator --fleet-version 1.5.0

# register the server (stdio)
claude mcp add amr -- uv run --project /path/to/amr-emulator amr-mcp
```

Claude Desktop (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "amr": {
      "command": "uv",
      "args": ["run", "--project", "/path/to/amr-emulator", "amr-mcp"],
      "env": {"AMR_ROBOT_URL": "http://127.0.0.1:8080"}
    }
  }
}
```

Then talk to it: *"pause the robot"*, *"queue the charging mission and wait
for it"*, *"inject an emergency stop and show me what the fleet sees"*.

## Against real hardware

Point `AMR_ROBOT_URL` at the robot's IP and set the account env vars.
State-changing tools move a real vehicle; the fault-injection tool answers
404 on hardware (it exists only on the emulator). Keep destructive-tool
confirmation on in your client.

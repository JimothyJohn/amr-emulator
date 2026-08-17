# mir-mcp

MCP (Model Context Protocol) server that lets any MCP client — Claude Code,
Claude Desktop, or anything else speaking MCP — control MiR robots and
fleets in natural language. It wraps the documented MiR REST APIs (robot
`/api/v2.0.0`, fleet `/api/v1`), so it works identically against this
repo's emulator and against real hardware.

## Tools

Discovery: `mir_discover_robots` — find robots on the network by IP when you
don't know an address: sweeps candidate hosts (a CIDR, host list, or the
local /24 by default) on ports 80/8080 and returns every confirmed MiR
target with its kind and software version. Then set `MIR_ROBOT_URL` /
`MIR_FLEET_URL` to a found URL.

`mir_server_info` — identifies what the configured URLs point at
(robot, fleet, or the multi-version demo dispatcher) and which MiR software
version each target reports. The other tools run the same handshake on
their first call, so pointing `MIR_ROBOT_URL` at a dispatcher root just
works: the newest served version is used unless `MIR_VERSION` /
`MIR_FLEET_VERSION` pins one. No version needs to be installed or
configured to match the target.

Robot: `mir_robot_status`, `mir_set_robot_state` (ready/pause/manual),
`mir_clear_error`, `mir_list_missions`, `mir_queue_mission` (by name or
guid, optional wait-for-completion), `mir_mission_queue`,
`mir_cancel_missions`, `mir_wait_for` (server-side wait on a condition —
queue idle, state, errors cleared, battery threshold — with progress
notifications), `mir_read_register`, `mir_write_register`,
`mir_manage_faults` (emulator-only fault injection).

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
- **Server-side waits.** `mir_wait_for` replaces agent-side polling
  loops: one call that polls the robot, streams progress notifications,
  and returns the observed state transitions plus the final status.
- **Live status resource.** `mir://robot/status` serves the trimmed
  status document; `mir_wait_for` announces resource updates on every
  observed state change.
- **Instructions & caching.** The server ships initialize-time
  instructions (workflow, guardrails) and marks its static tool/resource
  lists cacheable.

Fleet: `mir_fleet_robots`, `mir_fleet_dispatch` (serial orders by mission
name), `mir_fleet_order_status` (check/abort).

## Configuration (environment)

| Variable | Default | Meaning |
|---|---|---|
| `MIR_ROBOT_URL` | `http://127.0.0.1:8080` | Robot base URL |
| `MIR_FLEET_URL` | = `MIR_ROBOT_URL` | Fleet base URL |
| `MIR_USERNAME` / `MIR_PASSWORD` | `distributor` | Robot account (password pre-hash) |
| `MIR_API_KEY` | `distributor` | Fleet `x-api-key` |
| `MIR_SESSION` | unset | Emulator-only `X-MiR-Session` isolation id |
| `MIR_VERSION` | newest served | Robot version to pin when the URL is a multi-version dispatcher |
| `MIR_FLEET_VERSION` | newest served | Fleet version to pin, same case |

## Use with Claude Code

```sh
# terminal 1: something to control
uv run mir-emulator --fleet-version 1.5.0

# register the server (stdio)
claude mcp add mir -- uv run --project /path/to/mir-emulator mir-mcp
```

Claude Desktop (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "mir": {
      "command": "uv",
      "args": ["run", "--project", "/path/to/mir-emulator", "mir-mcp"],
      "env": {"MIR_ROBOT_URL": "http://127.0.0.1:8080"}
    }
  }
}
```

Then talk to it: *"pause the robot"*, *"queue the charging mission and wait
for it"*, *"inject an emergency stop and show me what the fleet sees"*.

## Against real hardware

Point `MIR_ROBOT_URL` at the robot's IP and set the account env vars.
State-changing tools move a real vehicle; the fault-injection tool answers
404 on hardware (it exists only on the emulator). Keep destructive-tool
confirmation on in your client.

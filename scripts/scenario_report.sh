#!/usr/bin/env bash
# Replay a scenario on a throwaway emulator and render its amr-report
# dashboard to a self-contained HTML file.
#
#   ./scripts/scenario_report.sh                                  # machine-shop day
#   ./scripts/scenario_report.sh scenarios/denso_jit_callbuttons.py
#   ./scripts/scenario_report.sh scenarios/fm_logistic_endurance.py fm.html
#
# Env knobs: PORT (default 8143), SESSION (override the auto-detected
# X-AMR-Session), NO_OPEN=1 (don't open the HTML when done).
#
# Emulator state is in-memory, so the scenario is always replayed fresh.
# The report reads one session — for multi-robot scenarios (whirlpool,
# dhl) the first session in the file wins unless SESSION says otherwise.
# stellantis_fleet_dispatch.py wants a fleet emulator; not supported here.

set -e
set -o nounset
set -o pipefail

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

SCENARIO="${1:-scenarios/machineshop_barfeed_lathes.py}"
STEM="$(basename "${SCENARIO}" .py)"
OUTPUT="${2:-${STEM}-report.html}"
PORT="${PORT:-8143}"

[ -f "${SCENARIO}" ] || { echo "no such scenario: ${SCENARIO}" >&2; exit 1; }

# Each scenario hardcodes its X-AMR-Session in a client("...") call.
SESSION="${SESSION:-$(grep -o 'client("[^"]*")' "${SCENARIO}" | head -1 | cut -d'"' -f2)}"
[ -n "${SESSION}" ] || { echo "could not detect a session in ${SCENARIO}; set SESSION=" >&2; exit 1; }

if curl -sf "http://127.0.0.1:${PORT}/" >/dev/null 2>&1; then
    echo "port ${PORT} already in use; set PORT= to a free one" >&2
    exit 1
fi

EMU_LOG="$(mktemp -t amr-emulator-report)"
uv run amr-emulator --port "${PORT}" --mission-duration 2 >"${EMU_LOG}" 2>&1 &
EMU_PID=$!
trap 'kill "${EMU_PID}" 2>/dev/null || true; wait "${EMU_PID}" 2>/dev/null || true' EXIT

for _ in $(seq 1 30); do
    curl -sf "http://127.0.0.1:${PORT}/" >/dev/null 2>&1 && break
    sleep 1
done
curl -sf "http://127.0.0.1:${PORT}/" >/dev/null 2>&1 || {
    echo "emulator failed to boot; log: ${EMU_LOG}" >&2
    exit 1
}
log "emulator up on :${PORT}, replaying ${SCENARIO} (session '${SESSION}')"

AMR_URL="http://127.0.0.1:${PORT}" uv run "${SCENARIO}"

log "rendering dashboard"
uv run amr-report "http://127.0.0.1:${PORT}" --session "${SESSION}" -o "${OUTPUT}"

log "dashboard written to ${OUTPUT}"
if [ -z "${NO_OPEN:-}" ] && command -v open >/dev/null 2>&1; then
    open "${OUTPUT}"
fi

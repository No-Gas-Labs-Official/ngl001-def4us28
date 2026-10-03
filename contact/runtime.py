#!/usr/bin/env python3
import hashlib, json, urllib.request
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parents[1]
state_path = root / "contact/state.json"
ledger_path = root / "contact/ledger.jsonl"
state = json.loads(state_path.read_text())

if not state.get("enabled"):
    raise SystemExit("CONTACT disabled by founder")

with urllib.request.urlopen(
    "https://api.github.com/repos/No-Gas-Labs-Official/ngl001-def4us28",
    timeout=20,
) as response:
    observed = json.loads(response.read().decode())

observation = {
    "type": "EXTERNAL_OBSERVATION",
    "source": "github-rest-api",
    "full_name": observed.get("full_name"),
    "default_branch": observed.get("default_branch"),
}
previous = state.get("last_event_hash")
event = {
    "schema": "ngl.contact.event.v1",
    "event_id": f"run-{int(state.get('run_count', 0)) + 1}",
    "observed_at": datetime.now(timezone.utc).isoformat(),
    "caused_by": "AUTONOMOUS_SCHEDULED_STEPWIRE",
    "epistemic_type": "EXTERNAL_OBSERVATION",
    "observation": observation,
    "previous_event_hash": previous,
}
canonical = json.dumps(event, sort_keys=True, separators=(",", ":"))
event_hash = hashlib.sha256(canonical.encode()).hexdigest()
event["event_hash"] = event_hash
with ledger_path.open("a") as ledger:
    ledger.write(json.dumps(event, sort_keys=True) + "\n")

state["run_count"] = int(state.get("run_count", 0)) + 1
state["last_event_hash"] = event_hash
state["last_observation"] = observation
state["phase"] = "OBSERVED"
state["next_transition"] = "AWAIT_FOUNDER_OR_NEXT_STEPWIRE"
state_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
print(json.dumps({"event_hash": event_hash, "observation": observation}, sort_keys=True))

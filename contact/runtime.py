#!/usr/bin/env python3
import json, urllib.request
from pathlib import Path
root=Path(__file__).resolve().parents[1]
state_path=root/'contact/state.json'
state=json.loads(state_path.read_text())
if not state.get('enabled'): raise SystemExit('CONTACT disabled by founder')
with urllib.request.urlopen('https://api.github.com/repos/No-Gas-Labs-Official/ngl001-def4us28', timeout=20) as response:
    observed=json.loads(response.read().decode())
state['run_count']=int(state.get('run_count',0))+1
state['last_observation']={'type':'EXTERNAL_OBSERVATION','full_name':observed.get('full_name'),'default_branch':observed.get('default_branch')}
state['phase']='OBSERVED'; state['next_transition']='AWAIT_FOUNDER_OR_NEXT_STEPWIRE'
state_path.write_text(json.dumps(state,indent=2,sort_keys=True)+'\n')
print(json.dumps(state['last_observation'],sort_keys=True))

#!/usr/bin/env python3
import hashlib,json,tempfile,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
def h(e):
 d={k:v for k,v in e.items() if k!="event_hash"}
 return hashlib.sha256(json.dumps(d,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def event(i,t,actor="LAB",refs=None,prev=None):
 e={"event_id":i,"experiment_id":"NEG","objective_id":None,"capability_id":None,"authorization_id":None,"timestamp":"2026-10-03T00:00:00Z","actor":"test","actor_class":actor,"event_type":t,"subject":"negative-test","claim":"","evidence_refs":refs or [],"authority_refs":[],"previous_hash":prev,"event_hash":None}
 e["event_hash"]=h(e); return e
def rejected(events):
 with tempfile.NamedTemporaryFile("w",delete=False) as f:
  for e in events:f.write(json.dumps(e)+"\n")
  p=f.name
 return subprocess.run([sys.executable,str(HERE/"validate_ledger.py"),p],capture_output=True).returncode!=0
cases={}
e=event("x","AUTHORIZED","CONTACT",["founder_authority_object"]); cases["model_authored_allow"]=rejected([e])
a=event("a","OBSERVATION"); b=event("b","OBSERVATION",prev="forged"); cases["broken_hash_chain"]=rejected([a,b])
e=event("x","CAPABILITY_VERIFIED",refs=[]); cases["verification_without_receipt"]=rejected([e])
e=event("x","ACTION_VERIFIED",refs=[]); cases["action_without_post_observation"]=rejected([e])
e=event("x","OBJECTIVE_VERIFIED",refs=["verification_probe"]); cases["probe_laundering"]=rejected([e])
print(json.dumps(cases,indent=2))
raise SystemExit(not all(cases.values()))

# REFLEXIVE-ADAPTATION-001 pressure: implementation identity changed; prior execution evidence must not verify this revision.

#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path

FORBIDDEN={
 "CAPABILITY_VERIFIED":("verifier_receipt","implementation_identity"),
 "ACTION_COMPLETED":("executor_receipt",),
 "ACTION_VERIFIED":("post_action_external_observation",),
 "OBJECTIVE_VERIFIED":("fresh_external_observation",),
 "AUTHORIZED":("founder_authority_object",),
}
def canonical(e):
 d={k:v for k,v in e.items() if k!="event_hash"}
 return json.dumps(d,sort_keys=True,separators=(",",":"))
def validate(events):
 errors=[]; prev=None; evidence=set()
 for i,e in enumerate(events):
  tag=f"event[{i}]"
  if e.get("previous_hash")!=prev: errors.append(f"{tag}: broken previous_hash")
  calc=hashlib.sha256(canonical(e).encode()).hexdigest()
  if e.get("event_hash")!=calc: errors.append(f"{tag}: invalid event_hash")
  refs=e.get("evidence_refs",[])
  missing=[x for x in refs if x not in evidence]
  if missing: errors.append(f"{tag}: missing evidence refs {missing}")
  for req in FORBIDDEN.get(e.get("event_type"),()):
   if req not in refs: errors.append(f"{tag}: {e.get('event_type')} lacks {req}")
  if e.get("event_type")=="AUTHORIZED" and e.get("actor_class")!="FOUNDER":
   errors.append(f"{tag}: non-founder authorization")
  if e.get("event_type")=="OBJECTIVE_VERIFIED" and "verification_probe" in refs:
   errors.append(f"{tag}: verifier probe reused as objective evidence")
  eid=e.get("event_id")
  if eid: evidence.add(eid)
  prev=e.get("event_hash")
 return errors
if __name__=="__main__":
 events=[json.loads(x) for x in Path(sys.argv[1]).read_text().splitlines() if x.strip()]
 errs=validate(events)
 print(json.dumps({"valid":not errs,"errors":errs},indent=2))
 raise SystemExit(bool(errs))

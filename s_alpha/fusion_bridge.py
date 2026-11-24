"""Trusted local callable for an external orchestrator; no implicit signing."""
from .fusion_authorization import authorized_dispatch,verify_evidence

def execute_v3(task,signature,key,root,db,*,allowed=()):
    evidence=authorized_dispatch(task,signature,key,root,db,allowed=allowed)
    if not verify_evidence(evidence,key):
        raise ValueError("invalid execution evidence")
    return evidence

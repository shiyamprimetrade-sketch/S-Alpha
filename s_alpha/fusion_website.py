"""Generate a bounded, offline, static website from structured text."""
from html import escape
from .create import create

def build_website(spec, root):
    if not isinstance(spec,dict) or set(spec)!={"title","heading","paragraphs"}:
        raise ValueError("invalid website specification")
    title,heading,paragraphs=spec["title"],spec["heading"],spec["paragraphs"]
    if not all(isinstance(v,str) and 0<len(v)<=200 for v in (title,heading)):
        raise ValueError("invalid heading")
    if not isinstance(paragraphs,list) or not 1<=len(paragraphs)<=20 or any(not isinstance(p,str) or len(p)>2000 for p in paragraphs):
        raise ValueError("invalid paragraphs")
    body="".join("<p>"+escape(p)+"</p>" for p in paragraphs)
    page='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+escape(title)+'</title><style>body{font:18px system-ui;max-width:720px;margin:auto;padding:24px;line-height:1.6;color:#172033;background:#f8fafc}h1{color:#164e63}</style></head><body><main><h1>'+escape(heading)+'</h1>'+body+'</main></body></html>'
    return {"status":"generated","artifact":create(root,"index.html",page)}

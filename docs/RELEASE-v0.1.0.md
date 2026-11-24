# v0.1.0 release candidate
Local Python 3.11+ prototype. Four built-in templates, controlled addition repair, SQLite evidence, supervised strategy selection, promotion audit, CLI and structured local API.
Prior CI 45452227764 passed including CLI demonstration. New API tests pending.
Security review: built-in source only; exclusive file creation prevents ordinary overwrites; no shell execution; caller must control workspace and database paths. Not a sandbox or hostile multi-user service. Claims persist after failure; filesystem and database writes are not atomic. No general AI or independent real-world benchmark. Omega approval and Android validation pending.
Release gate: latest CI must pass before merge.

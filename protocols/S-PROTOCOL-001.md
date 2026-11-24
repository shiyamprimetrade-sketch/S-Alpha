# Draft v1 — ALPHA-009
Legacy create_text: version=1, id, operation=create_text, name, content.
Software task: version=1, id, operation=build_software, requirement (string).
Public runner: s_alpha.runner.run(task, root, db). Single-use IDs per database.
Success: version, id, status=verified, kind, artifact (name, sha256), verification.
Failures currently raise exceptions; structured error envelope remains pending. No shell execution or arbitrary user source. Local root and database are caller-configured trusted paths.
Omega approval and upstream adapters pending. This is a proposal, not a ratified shared contract.

# S-Alpha — integrated v0.2 prototype baseline

S-Create, S-Learn and S-Universal provide bounded arithmetic synthesis, verification, single-operator repair, persistent knowledge and local orchestration. Python 3.11+; no third-party runtime dependencies.

## Quick start
```sh
python -m unittest discover -s tests -v
python -m s_alpha.doctor
python -m benchmarks.acceptance
python -m s_alpha execute examples/synthesis.json
python -m s_alpha.ui
```
Open http://127.0.0.1:8766. Task IDs are single-use. Android: see [Termux guide](docs/ANDROID.md).

## Evidence and scope
[Release candidate record](docs/RELEASE-v0.2.0.md) | [Security boundary](docs/SECURITY.md) | [Protocol v2](protocols/S-PROTOCOL-002.md) | [Final checkpoint](checkpoints/ALPHA-022.md)

PR #2 merged after Ubuntu and Windows CI passed on its head. Physical Android acceptance deferred. Adaptive repair is experimental and disabled by default. Not a general autonomous programmer or production server. No license granted by this README; public repository is not confidential.

# S-Alpha
Local experimental prototypes of S-Create, S-Learn and S-Universal. Python 3.11+, standard library only. Not a general autonomous AI.

## Quick start
From repository root:
```sh
python -m s_alpha train benchmarks/training_demo.json
python -m s_alpha strategy
python -m s_alpha build "Build addition!" --id demo001
python -m s_alpha history demo001
python -m unittest discover -s tests -v
```
Use a fresh task ID and output directory for each build of the same template. The default database is alpha.sqlite3; specify --db before the command to change it.

## Components
- S-Create: calculator, temperature, counter, addition templates; controlled addition repair and self-tests.
- S-Learn: SQLite execution evidence, strategy selection and promotion audit.
- S-Universal: versioned routing, bounded retries, CLI task claims.
- protocols/: proposed shared interface; Omega approval pending.
- checkpoints/: engineering record; benchmarks/: synthetic evaluation.

## Limitations
No arbitrary source execution, neural training, general software generation, atomic filesystem/database transaction or upstream adapters. Single-use IDs remain claimed after failure. Physical Android validation pending. Public repository: no secrets or unpublished patent-sensitive material. No license granted by this README.

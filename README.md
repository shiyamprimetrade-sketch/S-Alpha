# S-Alpha

Project S engineering workspace for S-Create, S-Learn and S-Universal.

## Status
Experimental prototypes; not a production autonomous AI. Public repository: do not publish secrets or unpublished patent-sensitive research.

## Architecture
- `s_alpha/create.py`: bounded artifact creation.
- `s_alpha/learn.py`: persistent evaluation records.
- `s_alpha/universal.py`: versioned task routing.
- `protocols/`: shared interface proposal.
- `tests/`: regression tests.
- `docs/`, `research/`, `experiments/`, `benchmarks/`, `checkpoints/`: engineering evidence.

## Run
Python 3.11+; no third-party runtime dependencies.

```sh
python -m unittest discover -s tests -v
```

## Existing foundations
S, S-Eye, S-Hand and S_Ml remain separate upstream projects. Integration adapters are pending source audit.

## Governance
Founder-approved public monorepo; zero additional budget. No license granted by this README. Contributions and releases require review.

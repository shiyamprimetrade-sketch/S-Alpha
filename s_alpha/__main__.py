import argparse
import json
from .runner import run
from .learn import history, feedback

def main():
    p = argparse.ArgumentParser(description="S-Alpha local prototype")
    p.add_argument("--db", default="alpha.sqlite3")
    sub = p.add_subparsers(dest="command", required=True)
    b = sub.add_parser("build")
    b.add_argument("requirement")
    b.add_argument("--id", required=True)
    b.add_argument("--out", default="workspace")
    h = sub.add_parser("history")
    h.add_argument("id")
    a = p.parse_args()
    try:
        if a.command == "build":
            result = run(dict(version=1, operation="build_software", id=a.id, requirement=a.requirement), a.out, a.db)
        else:
            result = {"events": history(a.db,a.id), "feedback": feedback(a.db,a.id)}
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, RuntimeError, OSError) as exc:
        p.exit(1, str(exc)+"\n")

if __name__ == "__main__":
    raise SystemExit(main())

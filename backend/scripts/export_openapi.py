"""Write docs/openapi.yaml (Swagger/OpenAPI 3.1) from the running app's route definitions.

    python scripts/export_openapi.py

The spec is generated from the code, so it cannot drift from the implementation:
  * every route lists its error responses (400/401/403/404/409/422/502) with the ErrorResponse schema
  * every route carries `x-user-stories` and a "User stories" line in its description
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DATABASE_URL", "sqlite://")  # no database connection is needed to build the spec

import yaml  # noqa: E402

from app.main import app  # noqa: E402


def main() -> None:
    spec = app.openapi()
    out = ROOT / "docs" / "openapi.yaml"
    out.parent.mkdir(exist_ok=True)
    out.write_text(yaml.safe_dump(spec, sort_keys=False, allow_unicode=True, width=100), encoding="utf-8")
    ops = sum(len(v) for v in spec["paths"].values())
    print(f"Wrote {out.relative_to(ROOT)}: {len(spec['paths'])} paths, {ops} operations")


if __name__ == "__main__":
    main()

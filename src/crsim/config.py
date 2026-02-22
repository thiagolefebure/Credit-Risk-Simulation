from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Paths:
    root: Path
    data_dir: Path
    synthetic_dir: Path
    reports_dir: Path
    figures_dir: Path
    sql_dir: Path

def get_paths() -> Paths:
    root = Path(__file__).resolve().parents[2]  # repo root
    data_dir = root / "data"
    synthetic_dir = data_dir / "synthetic"
    reports_dir = root / "reports"
    figures_dir = reports_dir / "figures"
    sql_dir = root / "sql"
    synthetic_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    return Paths(root, data_dir, synthetic_dir, reports_dir, figures_dir, sql_dir)

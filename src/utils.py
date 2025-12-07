import yaml
from pathlib import Path
from typing import Any, Dict


def load_config(path: str | Path) -> Dict[str, Any]:
    """Load a YAML configuration file."""
    path = Path(path)
    with path.open("r") as f:
        cfg = yaml.safe_load(f)
    return cfg


def resolve_path(base: str | Path, *parts: str | Path) -> Path:
    """Join and normalize paths relative to a base directory."""
    return Path(base).joinpath(*parts).expanduser().resolve()


def ensure_dir(path: str | Path) -> Path:
    """Create directory if it does not exist and return it as Path."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p



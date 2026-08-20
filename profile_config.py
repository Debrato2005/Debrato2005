from pathlib import Path
from typing import Any

import yaml


def load_profile(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)
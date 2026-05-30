"""Configuration loader."""
import yaml
from pathlib import Path
from typing import Any, Dict

def load_config(config_name: str = "default.yaml") -> Dict[str, Any]:
    """Load YAML configuration from config/ directory."""
    config_path = Path(__file__).parents[3] / "config" / config_name
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)
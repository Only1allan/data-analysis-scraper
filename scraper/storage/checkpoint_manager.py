import json
from pathlib import Path
from typing import Any, Dict


class CheckpointManager:
    """Manages checkpoints to resume scraping."""

    def __init__(self, path: str):
        self.path = Path(path)
        self.data: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """Load checkpoint data from file."""
        if not self.path.exists():
            self.data = {}
            return

        try:
            with open(self.path, "r") as f:
                self.data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading checkpoint: {e}")
            self.data = {}

    def save(self) -> None:
        """Save checkpoint data to file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.path, "w") as f:
                json.dump(self.data, f, indent=2)
        except IOError as e:
            print(f"Error saving checkpoint: {e}")

    def __getitem__(self, key: str) -> Any:
        return self.data.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.data[key] = value
        # Auto-save on updates to prevent data loss
        if len(self.data) % 10 == 0:
            self.save()

    def __contains__(self, key: str) -> bool:
        return key in self.data

    def values(self):
        return self.data.values()

    def get_all(self) -> Dict[str, Any]:
        """Get all checkpoint data."""
        return self.data
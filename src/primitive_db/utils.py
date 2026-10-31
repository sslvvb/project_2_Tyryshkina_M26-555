import json
from os import PathLike


def load_metadata(filepath: str | PathLike[str]) -> dict[str, list[str]]:
    """Load table schemas, returning an empty database for a missing file."""
    try:
        with open(filepath, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(
    filepath: str | PathLike[str], data: dict[str, list[str]]
) -> None:
    """Persist table schemas as readable JSON."""
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")

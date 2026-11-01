import json
from os import PathLike
from pathlib import Path

from primitive_db.constants import DATA_DIR
from primitive_db.types import TableData


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


def load_table_data(table_name: str) -> TableData:
    """Read rows from the table's JSON file."""
    path = table_path(table_name)
    try:
        with path.open(encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return []
    if not isinstance(data, list) or any(not isinstance(row, dict) for row in data):
        raise ValueError(f"Повреждены данные таблицы {table_name}")
    return data


def save_table_data(table_name: str, data: TableData) -> None:
    """Create the data directory and persist rows."""
    path = table_path(table_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")


def table_path(table_name: str) -> Path:
    """Return the data file path for a valid table name."""
    if not table_name.isidentifier():
        raise ValueError(table_name)
    return Path(DATA_DIR) / f"{table_name}.json"


def remove_table_data(table_name: str) -> None:
    """Remove a dropped table's data file if it exists."""
    table_path(table_name).unlink(missing_ok=True)

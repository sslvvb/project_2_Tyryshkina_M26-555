import json
from copy import deepcopy

from primitive_db.constants import PYTHON_TYPES, SUPPORTED_TYPES
from primitive_db.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)
from primitive_db.types import Metadata, Row, TableData, Value
from primitive_db.utils import load_table_data

_cache_select = create_cacher()


@handle_db_errors
def create_table(
    metadata: dict[str, list[str]], table_name: str, columns: list[str]
) -> dict[str, list[str]]:
    """Validate a schema and add it to metadata."""
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    schema = ["ID:int"]
    names = {"ID"}
    explicit_id = False
    for column in columns:
        parts = column.split(":")
        if len(parts) != 2:
            raise ValueError(column)
        name, data_type = parts
        if not name.isidentifier() or data_type not in SUPPORTED_TYPES:
            raise ValueError(column)
        if name == "ID" and data_type == "int" and not explicit_id:
            explicit_id = True
            continue
        if name in names:
            raise ValueError(column)
        names.add(name)
        schema.append(column)

    if not table_name.isidentifier() or not columns:
        raise ValueError(table_name)
    metadata[table_name] = schema
    print(
        f'Таблица "{table_name}" успешно создана со столбцами: '
        + ", ".join(schema)
    )
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(
    metadata: dict[str, list[str]], table_name: str
) -> dict[str, list[str]]:
    """Remove an existing table from metadata."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata
    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def table_schema(metadata: Metadata, table_name: str) -> dict[str, str]:
    """Return column types for an existing table."""
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует')
    return dict(column.split(":") for column in metadata[table_name])


def validate_fields(schema: dict[str, str], fields: Row) -> None:
    """Reject unknown columns and values that do not match the schema."""
    for column, value in fields.items():
        if column not in schema:
            raise ValueError(f'Столбец "{column}" не существует')
        if type(value) is not PYTHON_TYPES[schema[column]]:
            raise ValueError(f'{column}={value!r}: ожидается {schema[column]}')


@handle_db_errors
@log_time
def insert(metadata: Metadata, table_name: str, values: list[Value]) -> TableData:
    """Validate values and append a row with an automatically generated ID."""
    schema = table_schema(metadata, table_name)
    columns = [column for column in schema if column != "ID"]
    if len(values) != len(columns):
        raise ValueError(f"Ожидается значений: {len(columns)}, получено: {len(values)}")
    row = dict(zip(columns, values, strict=True))
    validate_fields(schema, row)
    table_data = load_table_data(table_name)
    next_id = max((record["ID"] for record in table_data), default=0) + 1
    table_data.append({"ID": next_id, **row})
    return table_data


@handle_db_errors
@log_time
def select(table_data: TableData, where_clause: Row | None = None) -> TableData:
    # Data is part of the key: inserts, updates, deletes and external file
    # changes cannot return a result cached for an older table snapshot.
    """Return isolated, cached rows matching an optional equality condition."""
    key = json.dumps([table_data, where_clause], sort_keys=True, ensure_ascii=False)

    def get_rows() -> TableData:
        """Compute a fresh query result for the current table snapshot."""
        if where_clause is None:
            return deepcopy(table_data)
        return deepcopy([
            row for row in table_data
            if all(row.get(column) == value for column, value in where_clause.items())
        ])

    # Callers must not be able to change the cached rows through the result.
    return deepcopy(_cache_select(key, get_rows))


@handle_db_errors
def update(table_data: TableData, set_clause: Row, where_clause: Row) -> TableData:
    """Update matching rows while preserving their generated IDs."""
    if "ID" in set_clause:
        raise ValueError("ID генерируется автоматически и не может быть изменён")
    for row in table_data:
        if all(row.get(column) == value for column, value in where_clause.items()):
            row.update(set_clause)
    return table_data


@handle_db_errors
@confirm_action("удаление записей")
def delete(table_data: TableData, where_clause: Row) -> TableData:
    """Return rows remaining after confirmed deletion."""
    return [
        row for row in table_data
        if not all(row.get(column) == value for column, value in where_clause.items())
    ]

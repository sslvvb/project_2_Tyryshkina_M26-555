SUPPORTED_TYPES = {"int", "str", "bool"}


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

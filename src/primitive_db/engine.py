import json
import shlex

import prompt
from prettytable import PrettyTable

from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    insert,
    select,
    table_schema,
    update,
    validate_fields,
)
from primitive_db.parser import parse_set, parse_values, parse_where, tokenize
from primitive_db.types import Metadata
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
    table_path,
)

METADATA_FILE = "db_meta.json"


def print_help() -> None:
    """Prints the help message for the current mode."""

    print("***Операции с данными***")
    print("Функции:")
    print(
        "<command> create_table <имя_таблицы> <столбец1:тип> "
        "<столбец2:тип> .. - создать таблицу"
    )
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print(
        "<command> insert into <имя_таблицы> values (<значение1>, ...) "
        "- создать запись"
    )
    print("<command> select from <имя_таблицы> - прочитать все записи")
    print(
        "<command> select from <имя_таблицы> where <столбец> = <значение> "
        "- прочитать записи по условию"
    )
    print(
        "<command> update <имя_таблицы> set <столбец> = <новое_значение> "
        "where <столбец_условия> = <значение_условия> - обновить записи"
    )
    print(
        "<command> delete from <имя_таблицы> where <столбец> = <значение> "
        "- удалить записи"
    )
    print("<command> info <имя_таблицы> - вывести информацию о таблице")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация")


def execute_data_command(user_input: str, metadata: Metadata) -> None:
    """Parse a CRUD command, validate it and persist its result."""
    tokens = tokenize(user_input)
    where_clause = None
    set_clause = None
    values = None
    match tokens:
        case ["insert", "into", table_name, "values", *value_tokens]:
            operation = "insert"
            values = parse_values(value_tokens)
        case ["select", "from", table_name]:
            operation = "select"
        case ["select", "from", table_name, "where", *condition]:
            operation = "select"
            where_clause = parse_where(" ".join(condition))
        case ["update", table_name, "set", *clauses] if "where" in clauses:
            operation = "update"
            boundary = clauses.index("where")
            set_clause = parse_set(" ".join(clauses[:boundary]))
            where_clause = parse_where(" ".join(clauses[boundary + 1:]))
        case ["delete", "from", table_name, "where", *condition]:
            operation = "delete"
            where_clause = parse_where(" ".join(condition))
        case ["info", table_name]:
            operation = "info"
        case _:
            raise ValueError(user_input)

    schema = table_schema(metadata, table_name)
    if where_clause is not None:
        validate_fields(schema, where_clause)
    if set_clause is not None:
        validate_fields(schema, set_clause)
        if "ID" in set_clause:
            raise ValueError("ID генерируется автоматически и не может быть изменён")

    if operation == "insert":
        data = insert(metadata, table_name, values)
        save_table_data(table_name, data)
        print(
            f'Запись с ID={data[-1]["ID"]} успешно добавлена '
            f'в таблицу "{table_name}".'
        )
        return

    data = load_table_data(table_name)
    if operation == "select":
        result = PrettyTable()
        result.field_names = list(schema)
        for row in select(data, where_clause):
            result.add_row([row[column] for column in schema])
        print(result)
    elif operation == "info":
        print(f"Таблица: {table_name}")
        print("Столбцы: " + ", ".join(metadata[table_name]))
        print(f"Количество записей: {len(data)}")
    else:
        matched = select(data, where_clause)
        if not matched:
            print("Записи по условию не найдены.")
            return
        if operation == "update":
            changed = update(data, set_clause, where_clause)
        else:
            changed = delete(data, where_clause)
        save_table_data(table_name, changed)
        for row in matched:
            if operation == "update":
                print(
                    f'Запись с ID={row["ID"]} в таблице "{table_name}" '
                    'успешно обновлена.'
                )
            else:
                print(
                    f'Запись с ID={row["ID"]} успешно удалена '
                    f'из таблицы "{table_name}".'
                )


def run() -> None:
    """Read commands and persist successful schema changes."""
    print()
    print_help()
    while True:
        try:
            metadata = load_metadata(METADATA_FILE)
        except (OSError, json.JSONDecodeError) as error:
            print(f"Ошибка чтения метаданных: {error}")
            return
        if not isinstance(metadata, dict):
            print("Ошибка: метаданные должны быть JSON-объектом.")
            return
        try:
            user_input = prompt.string("\n>>>Введите команду: ", empty=True)
        except (EOFError, KeyboardInterrupt):
            print()
            return
        try:
            command_name = (user_input or "").split(maxsplit=1)
            if command_name and command_name[0] in {
                "insert", "select", "update", "delete", "info"
            }:
                execute_data_command(user_input, metadata)
                continue
            args = shlex.split(user_input or "")
            if not args:
                continue
            command, *arguments = args
            if command in {"help", "exit", "list_tables"}:
                if arguments:
                    raise ValueError(" ".join(arguments))
                if command == "exit":
                    return
                if command == "help":
                    print_help()
                elif command == "list_tables":
                    if metadata:
                        for name in metadata:
                            print(f"- {name}")
                    else:
                        print("Таблиц пока нет.")
            elif command in {"create_table", "drop_table"}:
                if (command == "create_table" and len(arguments) < 2) or (
                    command == "drop_table" and len(arguments) != 1
                ):
                    raise ValueError(" ".join(args))
                previous = metadata.copy()
                if command == "create_table":
                    create_table(metadata, arguments[0], arguments[1:])
                else:
                    drop_table(metadata, arguments[0])
                if metadata != previous:
                    if command == "create_table":
                        save_table_data(arguments[0], [])
                    else:
                        table_path(arguments[0]).unlink(missing_ok=True)
                    save_metadata(METADATA_FILE, metadata)
            else:
                print(f"Функции {command} нет. Попробуйте снова.")
        except ValueError as error:
            print(f"Некорректное значение: {error}. Попробуйте снова.")
        except (OSError, json.JSONDecodeError) as error:
            print(f"Ошибка работы с файлами: {error}")

import json
import shlex

import prompt

from primitive_db.core import create_table, drop_table
from primitive_db.utils import load_metadata, save_metadata

METADATA_FILE = "db_meta.json"


def print_help() -> None:
    """Prints the help message for the current mode."""

    print("***Процесс работы с таблицей***")
    print("Функции:")
    print(
        "<command> create_table <имя_таблицы> <столбец1:тип> "
        "<столбец2:тип> .. - создать таблицу"
    )
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация")


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
                    save_metadata(METADATA_FILE, metadata)
            else:
                print(f"Функции {command} нет. Попробуйте снова.")
        except ValueError as error:
            print(f"Некорректное значение: {error}. Попробуйте снова.")
        except OSError as error:
            print(f"Ошибка сохранения метаданных: {error}")

# Primitive DB

## Управление таблицами

- `create_table <имя> <столбец:тип> ...` — создать таблицу.
- `list_tables` — показать таблицы.
- `drop_table <имя>` — удалить таблицу.
- `help` — показать справку.
- `exit` — выйти.

Поддерживаемые типы: `int`, `str`, `bool`. Столбец `ID:int` добавляется автоматически.

Пример сеанса:

```text
>>>Введите команду: create_table users name:str age:int is_active:bool
Таблица "users" успешно создана со столбцами: ID:int, name:str, age:int, is_active:bool
>>>Введите команду: list_tables
- users
>>>Введите команду: drop_table users
Таблица "users" успешно удалена.
>>>Введите команду: exit
```

## Демонстрация

[![Запись установки пакета и работы с таблицами](https://asciinema.org/a/SNsTmT5gSOY4Jwvj.svg)](https://asciinema.org/a/SNsTmT5gSOY4Jwvj)

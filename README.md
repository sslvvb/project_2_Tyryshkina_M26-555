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

## Демонстрация управления таблицами

[![Запись установки пакета и работы с таблицами](https://asciinema.org/a/SNsTmT5gSOY4Jwvj.png)](https://asciinema.org/a/SNsTmT5gSOY4Jwvj)

[Посмотреть запись на asciinema.org](https://asciinema.org/a/SNsTmT5gSOY4Jwvj)

## CRUD-операции

Перед добавлением записей создайте таблицу командой `create_table`.

- `insert into <таблица> values (<значение1>, <значение2>, ...)` — добавить запись.
- `select from <таблица>` — вывести все записи.
- `select from <таблица> where <столбец> = <значение>` — отобрать записи по условию.
- `update <таблица> set <столбец> = <значение> where <столбец> = <значение>` — обновить записи.
- `delete from <таблица> where <столбец> = <значение>` — удалить записи по условию.
- `info <таблица>` — показать столбцы и количество записей.

Все поля обязательны. В `insert` передаются значения в порядке столбцов без `ID`:
он генерируется автоматически как максимальный текущий ID плюс один.
Строки заключаются в одинарные или двойные кавычки, целые числа пишутся без кавычек,
логические значения — `true` и `false`. Типы значений должны соответствовать схеме.
`ID` нельзя изменять через `update`. В `set` можно перечислить несколько полей через
запятую. Условие `where` поддерживает одно сравнение на равенство.

Пример:

```text
create_table users name:str age:int is_active:bool
insert into users values ("Sergei", 28, true)
select from users where age = 28
update users set age = 29 where name = "Sergei"
select from users
info users
delete from users where ID = 1
info users
```

Данные сохраняются в `data/<имя_таблицы>.json` в каталоге запуска программы.

### Демонстрация CRUD

[![Запись установки и всех CRUD-операций](https://asciinema.org/a/W0TcESzgdY1mxylT.png)](https://asciinema.org/a/W0TcESzgdY1mxylT)

[Посмотреть запись CRUD на asciinema.org](https://asciinema.org/a/W0TcESzgdY1mxylT)

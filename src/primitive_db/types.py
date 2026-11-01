"""Types shared by storage, command parsing and database operations."""

type Value = str | int | bool
type Row = dict[str, Value]
type TableData = list[Row]
type Metadata = dict[str, list[str]]

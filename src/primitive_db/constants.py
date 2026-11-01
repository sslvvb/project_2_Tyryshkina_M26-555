"""Shared storage paths, schema types and command token syntax."""

META_FILE = "db_meta.json"
DATA_DIR = "data"
SUPPORTED_TYPES = {"int", "str", "bool"}
PYTHON_TYPES = {"int": int, "str": str, "bool": bool}
TOKEN_PATTERN = (
    r'''\s*("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|[A-Za-z_\u0080-\uffff]\w*|-?\d+|[(),=])'''
)

import ast
import re

from primitive_db.types import Row, Value

TOKEN = re.compile(
    r'''\s*("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|[A-Za-z_\u0080-\uffff]\w*|-?\d+|[(),=])'''
)


def tokenize(text: str) -> list[str]:
    """Split command text without losing quotes or punctuation in strings."""
    tokens = []
    position = 0
    while position < len(text):
        if not text[position:].strip():
            break
        match = TOKEN.match(text, position)
        if match is None:
            raise ValueError(text[position:])
        tokens.append(match.group(1))
        position = match.end()
    return tokens


def parse_value(token: str) -> Value:
    if token.startswith(('"', "'")):
        try:
            value = ast.literal_eval(token)
        except (SyntaxError, ValueError) as error:
            raise ValueError(token) from error
        if isinstance(value, str):
            return value
    elif token.lower() in {"true", "false"}:
        return token.lower() == "true"
    elif re.fullmatch(r"-?\d+", token):
        return int(token)
    raise ValueError(f"{token} (строковые значения должны быть в кавычках)")


def parse_where(text: str) -> Row:
    tokens = tokenize(text)
    if len(tokens) != 3 or not tokens[0].isidentifier() or tokens[1] != "=":
        raise ValueError(text)
    return {tokens[0]: parse_value(tokens[2])}


def parse_set(text: str) -> Row:
    tokens = tokenize(text)
    result = {}
    while tokens:
        if len(tokens) < 3:
            raise ValueError(text)
        column, equals, value = tokens[:3]
        if not column.isidentifier() or equals != "=" or column in result:
            raise ValueError(text)
        result[column] = parse_value(value)
        tokens = tokens[3:]
        if tokens:
            if tokens.pop(0) != "," or not tokens:
                raise ValueError(text)
    if not result:
        raise ValueError(text)
    return result


def parse_values(tokens: list[str]) -> list[Value]:
    if len(tokens) < 3 or tokens[0] != "(" or tokens[-1] != ")":
        raise ValueError("Ожидаются значения в круглых скобках")
    values = tokens[1:-1]
    if len(values) % 2 == 0 or any(token != "," for token in values[1::2]):
        raise ValueError("Значения должны быть разделены запятыми")
    return [parse_value(token) for token in values[::2]]

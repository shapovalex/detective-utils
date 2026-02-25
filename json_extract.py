import json
import re
import sys


def parse_path(path):
    """Parse a JSONPath string into a list of keys/indices.

    Supports:
      $.foo.bar        -> ["foo", "bar"]
      $.foo[0].bar     -> ["foo", 0, "bar"]
      $["key with spaces"]["deep value"] -> ["key with spaces", "deep value"]
    """
    if not path.startswith("$"):
        raise ValueError("Path must start with '$'")

    tokens = []
    # Strip the leading '$' and tokenize the rest
    rest = path[1:]

    token_re = re.compile(
        r'\["([^"]+)"\]'   # ["key with spaces"]
        r'|\.([^.\[]+)'    # .key
        r'|\[(\d+)\]'      # [0]
    )

    pos = 0
    while pos < len(rest):
        m = token_re.match(rest, pos)
        if not m:
            raise ValueError(f"Invalid path segment at position {pos + 1}: ...{rest[pos:]!r}")
        bracket_key, dot_key, index = m.groups()
        if bracket_key is not None:
            tokens.append(bracket_key)
        elif dot_key is not None:
            tokens.append(dot_key)
        else:
            tokens.append(int(index))
        pos = m.end()

    return tokens


def resolve_path(data, tokens):
    current = data
    for token in tokens:
        if isinstance(token, int):
            if not isinstance(current, list):
                raise TypeError(f"Expected list for index [{token}], got {type(current).__name__}")
            if token >= len(current) or token < -len(current):
                raise IndexError(f"Index [{token}] out of range (length {len(current)})")
            current = current[token]
        else:
            if not isinstance(current, dict):
                raise TypeError(f"Expected object for key {token!r}, got {type(current).__name__}")
            if token not in current:
                raise KeyError(f"Key {token!r} not found")
            current = current[token]
    return current


def load_json(source):
    try:
        with open(source) as f:
            raw = f.read()
    except OSError as e:
        print(f"Cannot open file: {e}", file=sys.stderr)
        sys.exit(1)
    return raw


def main():
    args = sys.argv[1:]

    if len(args) == 2:
        # json_extract.py <file> <path>
        raw = load_json(args[0])
        json_path = args[1]
    elif len(args) == 1:
        # json_extract.py <path>  — JSON from stdin
        print("Paste JSON input (press Ctrl+D when done):")
        raw = sys.stdin.read().strip()
        json_path = args[0]
    else:
        print("Usage:", file=sys.stderr)
        print("  python json_extract.py <file.json> <path>", file=sys.stderr)
        print("  python json_extract.py <path>          (JSON from stdin)", file=sys.stderr)
        print("", file=sys.stderr)
        print("Examples:", file=sys.stderr)
        print('  python json_extract.py data.json "$.company.name"', file=sys.stderr)
        print('  python json_extract.py data.json "$.employees[0].skills"', file=sys.stderr)
        print('  python json_extract.py data.json \'$["key with spaces"]\'', file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        tokens = parse_path(json_path)
    except ValueError as e:
        print(f"Invalid path: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        result = resolve_path(data, tokens)
    except (KeyError, IndexError, TypeError) as e:
        print(f"Path error: {e}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

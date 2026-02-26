import json
import sys

from jsonpath_ng import parse as jsonpath_parse
from jsonpath_ng.exceptions import JsonPathParserError


def extract(data, path):
    try:
        expr = jsonpath_parse(path)
    except JsonPathParserError as e:
        raise ValueError(str(e)) from e

    matches = expr.find(data)
    if not matches:
        raise KeyError(f"No match for path: {path!r}")

    values = [m.value for m in matches]
    return values[0] if len(values) == 1 else values


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
        result = extract(data, json_path)
    except (ValueError, KeyError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

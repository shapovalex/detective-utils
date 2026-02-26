import json
import sys


def _path_segment(key) -> str:
    if isinstance(key, int):
        return f"[{key}]"
    return f".{key}" if str(key).isidentifier() else f'["{key}"]'


def extract_paths(data) -> list[str]:
    """Return all JSONPath expressions that address a value in *data*."""

    def _recurse(obj, prefix: str) -> list[str]:
        paths = []
        if isinstance(obj, dict):
            for key, value in obj.items():
                path = prefix + _path_segment(key)
                paths.append(path)
                paths.extend(_recurse(value, path))
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                path = f"{prefix}[{i}]"
                paths.append(path)
                paths.extend(_recurse(item, path))
        return paths

    return _recurse(data, "$")


def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
        try:
            with open(path) as f:
                raw = f.read()
        except OSError as e:
            print(f"Cannot open file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Paste JSON input (press Ctrl+D when done):")
        raw = sys.stdin.read().strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    for path in extract_paths(data):
        print(path)


if __name__ == "__main__":
    main()

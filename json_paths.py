import json
import sys


def extract_paths(obj, prefix=""):
    paths = []

    if isinstance(obj, dict):
        for key in obj:
            safe_key = f'["{key}"]' if not key.isidentifier() else f".{key}"
            full_path = prefix + safe_key
            paths.append(full_path)
            paths.extend(extract_paths(obj[key], full_path))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            full_path = f"{prefix}[{i}]"
            paths.append(full_path)
            paths.extend(extract_paths(item, full_path))

    return paths


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

    paths = extract_paths(data, prefix="$")
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()

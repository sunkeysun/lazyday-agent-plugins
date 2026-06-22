#!/usr/bin/env bash
set -euo pipefail

PLUGIN_DIR="${1:-plugins/lazyday-coding}"
VALIDATOR="/Users/sunkeysun/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if "$PYTHON_BIN" -c "import yaml" >/dev/null 2>&1; then
  "$PYTHON_BIN" "$VALIDATOR" "$PLUGIN_DIR"
else
  YAML_SHIM_DIR="$(mktemp -d)"
  trap 'rm -rf "$YAML_SHIM_DIR"' EXIT
  cat >"$YAML_SHIM_DIR/yaml.py" <<'PY'
class YAMLError(Exception):
    pass


def safe_load(text):
    result = {}
    current_parent = None
    for raw_line in text.splitlines():
        if raw_line.startswith("  "):
            if current_parent is None:
                raise YAMLError(f"nested yaml line without parent: {raw_line}")
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" not in line:
                raise YAMLError(f"unsupported yaml line: {raw_line}")
            key, value = line.split(":", 1)
            result[current_parent][key.strip()] = _parse_scalar(value.strip())
            continue

        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise YAMLError(f"unsupported yaml line: {raw_line}")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value == "":
            result[key] = {}
            current_parent = key
        else:
            result[key] = _parse_scalar(value)
            current_parent = None
    return result


def _parse_scalar(value):
    if value in ("", "null", "None"):
        return None
    if value in ("true", "True"):
        return True
    if value in ("false", "False"):
        return False
    return value.strip("\"'")
PY
  PYTHONPATH="$YAML_SHIM_DIR${PYTHONPATH:+:$PYTHONPATH}" "$PYTHON_BIN" "$VALIDATOR" "$PLUGIN_DIR"
fi

if command -v claude >/dev/null 2>&1; then
  claude plugin validate "$PLUGIN_DIR"
else
  echo "skip Claude Code validation: claude command not found"
fi

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
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise YAMLError(f"unsupported yaml line: {raw_line}")
        key, value = line.split(":", 1)
        value = value.strip()
        if value in ("", "null", "None"):
            parsed = None
        elif value in ("true", "True"):
            parsed = True
        elif value in ("false", "False"):
            parsed = False
        else:
            parsed = value.strip("\"'")
        result[key.strip()] = parsed
    return result
PY
  PYTHONPATH="$YAML_SHIM_DIR${PYTHONPATH:+:$PYTHONPATH}" "$PYTHON_BIN" "$VALIDATOR" "$PLUGIN_DIR"
fi

if command -v claude >/dev/null 2>&1; then
  claude plugin validate "$PLUGIN_DIR"
else
  echo "skip Claude Code validation: claude command not found"
fi

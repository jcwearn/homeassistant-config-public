#!/usr/bin/env python3
"""Generate a mock secrets file so CI can resolve `!secret` references.

Replaces golles/mock-yaml-secrets-action. Scans a directory for YAML files,
collects every `!secret <name>` reference, and writes each one to the output
file with a fake value chosen by the first matching rule.
"""

import json
import os
import re
import sys

DEFAULT_CONFIG = {
    "directory": "./",
    "excludePaths": [],
    "secretFile": "secrets.yaml",
    "defaultValue": "value0123",
    "rules": {},
}

SECRET_PATTERN = re.compile(r"!secret (\w+)")


def read_config(path):
    with open(path, encoding="utf-8") as handle:
        return {**DEFAULT_CONFIG, **json.load(handle)}


def yaml_files(directory, exclude_paths):
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not excluded(os.path.join(root, d), exclude_paths)]
        for name in files:
            path = os.path.join(root, name)
            if os.path.splitext(name)[1] in (".yaml", ".yml") and not excluded(path, exclude_paths):
                yield path


def excluded(path, exclude_paths):
    return any(path.endswith(exclude) for exclude in exclude_paths)


def find_secrets(files):
    secrets = set()
    for path in files:
        with open(path, encoding="utf-8") as handle:
            secrets.update(SECRET_PATTERN.findall(handle.read()))
    return secrets


def apply_rules(secret, rules, default_value):
    for rule, value in rules.items():
        if re.search(rule, secret):
            return value
    return default_value


def main():
    if len(sys.argv) != 2:
        sys.exit(f"usage: {sys.argv[0]} <config-file>")

    config = read_config(sys.argv[1])
    secrets = find_secrets(yaml_files(config["directory"], config["excludePaths"]))

    with open(config["secretFile"], "w", encoding="utf-8") as handle:
        for secret in sorted(secrets):
            handle.write(f"{secret}: '{apply_rules(secret, config['rules'], config['defaultValue'])}'\n")

    print(f"Wrote {len(secrets)} mock secrets to {config['secretFile']}")


if __name__ == "__main__":
    main()

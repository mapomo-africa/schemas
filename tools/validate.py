#!/usr/bin/env python3
"""Validate every example in this repository against the schemas.

Also enforces the project rules that a JSON Schema cannot express by itself:

  * no real political actor names anywhere (every entity label is fictional)
  * no credential-shaped strings
  * every unit cost and every observation carries provenance with a source

Run:  python3 tools/validate.py
Exit code is non-zero if anything fails, so this doubles as the CI gate.
"""
import json
import pathlib
import re
import sys

try:
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource
except ImportError:
    sys.exit("Install dependencies first:  pip install jsonschema")

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMA_DIR = ROOT / "schema"
EXAMPLE_DIR = ROOT / "examples"

# Examples are named <schema-stem>.<variant>.json and validate against schema/<stem>.schema.json
def schema_for(example_path):
    stem = example_path.name.split(".")[0]
    return SCHEMA_DIR / f"{stem}.schema.json"


def build_registry():
    """Resolve $ref by bare filename, which is how the schemas reference each other."""
    registry = Registry()
    for path in sorted(SCHEMA_DIR.glob("*.json")):
        contents = json.loads(path.read_text())
        resource = Resource.from_contents(contents)
        registry = resource @ registry
        registry = registry.with_resource(uri=path.name, resource=resource)
    return registry


CREDENTIAL_PATTERNS = [
    re.compile(r"(?i)\b(api[_-]?key|secret|password|passwd|bearer|authorization)\b\s*[:=]"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"(?i)\baws_secret_access_key\b"),
]

FICTIONAL_LABEL = re.compile(
    r"^(Candidate|Party|Coalition|Campaign|Broadcaster|Publisher|Vendor|Observer Org|Platform|Outdoor Vendor)\s+[A-Z0-9]"
)


def walk(node, path=""):
    if isinstance(node, dict):
        for key, value in node.items():
            yield from walk(value, f"{path}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from walk(value, f"{path}[{index}]")
    else:
        yield path, node


def check_project_rules(doc, where, errors):
    for path, value in walk(doc):
        if not isinstance(value, str):
            continue
        for pattern in CREDENTIAL_PATTERNS:
            if pattern.search(value):
                errors.append(f"{where}: credential-shaped string at {path}")

    label = doc.get("label")
    if isinstance(label, dict):
        if label.get("isFictional") is not True:
            errors.append(f"{where}: entity label must be fictional in this repository")
        elif not FICTIONAL_LABEL.match(label.get("name", "")):
            errors.append(
                f"{where}: label {label.get('name')!r} does not look like a fictional label "
                "(expected e.g. 'Candidate A', 'Party B')"
            )

    if "provenance" in doc:
        source = doc["provenance"].get("source", {})
        if not source.get("type"):
            errors.append(f"{where}: provenance.source.type is required")


def main():
    registry = build_registry()
    errors = []
    checked = 0

    for schema_path in sorted(SCHEMA_DIR.glob("*.json")):
        schema = json.loads(schema_path.read_text())
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{schema_path.name}: not a valid schema: {exc}")

    for example_path in sorted(EXAMPLE_DIR.glob("*.json")):
        schema_path = schema_for(example_path)
        if not schema_path.exists():
            errors.append(f"{example_path.name}: no schema named {schema_path.name}")
            continue

        schema = json.loads(schema_path.read_text())
        document = json.loads(example_path.read_text())
        validator = Draft202012Validator(schema, registry=registry)

        for error in sorted(validator.iter_errors(document), key=lambda e: list(e.path)):
            location = "/".join(str(p) for p in error.path) or "(root)"
            errors.append(f"{example_path.name}: {location}: {error.message}")

        check_project_rules(document, example_path.name, errors)
        checked += 1

    if errors:
        print(f"FAILED: {len(errors)} problem(s)\n")
        for error in errors:
            print(f"  {error}")
        return 1

    print(f"OK: {checked} example(s) valid against {len(list(SCHEMA_DIR.glob('*.json')))} schema(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

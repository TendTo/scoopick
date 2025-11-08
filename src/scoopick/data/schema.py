import importlib.resources
import json
import sys
from enum import Enum

from jsonschema import Draft202012Validator, ValidationError

from .constants import PACKAGE_NAME


class Schema(Enum):
    POINTS = "points"


def load_schema(schema: Schema) -> dict:
    schema_name = f"{schema.value}_schema.json"
    if sys.version_info < (3, 9):
        with importlib.resources.open_text(PACKAGE_NAME, "resources", schema_name, encoding="utf-8") as schema_file:
            schema = json.load(schema_file)
    else:
        with (
            importlib.resources.files(PACKAGE_NAME)
            .joinpath("resources", schema_name)
            .open("r", encoding="utf-8") as schema_file
        ):
            schema = json.load(schema_file)
    return schema


def validate_data(schema: Schema, data: dict) -> bool:
    try:
        Draft202012Validator(load_schema(schema)).validate(instance=data)
        return True
    except ValidationError as e:
        print(f"Data validation error: {e.message}")
        return False

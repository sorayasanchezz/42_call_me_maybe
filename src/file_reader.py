import json
import sys
from typing import Any

from pydantic import ValidationError

from src.models import FunctionDefinition, PromptItem


def read_json_file(path: str) -> Any:
    """Open a JSON file and return its content.

    If the file cannot be read or is not valid JSON, show a clear
    error message and stop the program.

    Args:
        path: File to read.

    Returns:
        The JSON content.
    """
    try:
        with open(path, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        sys.exit(f"Error: file not found: {path}")
    except OSError as error:
        sys.exit(f"Error: cannot read {path}: {error}")
    except UnicodeDecodeError:
        sys.exit(f"Error: {path} is not a UTF-8 text file")
    except json.JSONDecodeError as error:
        sys.exit(f"Error: {path} is not valid JSON: {error}")


def load_functions(path: str) -> list[FunctionDefinition]:
    """Read the functions file and check every function with pydantic.

    Args:
        path: Functions file.

    Returns:
        The functions.
    """
    data = read_json_file(path)

    if not isinstance(data, list):
        sys.exit(f"Error: {path} must contain a list of functions")

    functions: list[FunctionDefinition] = []
    for item in data:
        try:
            functions.append(FunctionDefinition.model_validate(item))
        except ValidationError as error:
            sys.exit(f"Error: invalid function in {path}:\n{error}")

    if len(functions) == 0:
        sys.exit(f"Error: {path} does not contain any function")

    return functions


def load_prompts(path: str) -> list[PromptItem]:
    """Read the prompts file and check every prompt with pydantic.

    Args:
        path: Prompts file.

    Returns:
        The prompts.
    """
    data = read_json_file(path)

    if not isinstance(data, list):
        sys.exit(f"Error: {path} must contain a list of prompts")

    prompts: list[PromptItem] = []
    for item in data:
        try:
            prompts.append(PromptItem.model_validate(item))
        except ValidationError as error:
            sys.exit(f"Error: invalid prompt in {path}:\n{error}")

    return prompts

import json
import os
import sys
from typing import Any


def write_results(path: str, results: list[dict[str, Any]]) -> None:
    """Write the results in a JSON file.

    If the folder of the file does not exist, we create it.
    If the file cannot be written, show a clear error message
    and stop the program.

    Args:
        path: Output file.
        results: Results to write.
    """
    folder = os.path.dirname(path)

    try:
        if folder != "":
            os.makedirs(folder, exist_ok=True)
        with open(path, "w", encoding="utf-8") as file:
            json.dump(results, file, indent=2, ensure_ascii=False)
    except OSError as error:
        sys.exit(f"Error: cannot write {path}: {error}")

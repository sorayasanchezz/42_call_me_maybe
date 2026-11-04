import argparse
import sys
from typing import Any

try:
    from llm_sdk import Small_LLM_Model

    from src.file_reader import load_functions, load_prompts
    from src.file_writer import write_results
    from src.function_chooser import (
        choose_word,
        find_function,
        get_vocabulary,
    )
    from src.parameter_writer import write_all_parameters
    from src.prompt_builder import build_function_prompt
except KeyboardInterrupt:
    sys.exit("\nStopped by the user (Ctrl+C).")
except ImportError as error:
    sys.exit(f"Error: cannot load a module: {error}. Run 'make install'.")


def parse_arguments() -> argparse.Namespace:
    """Read the options written in the terminal.

    If an option is not written, its default value is used.

    Returns:
        The paths (defaults if not given).
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--functions_definition",
        default="data/input/functions_definition.json",
    )
    parser.add_argument(
        "--input",
        default="data/input/function_calling_tests.json",
    )
    parser.add_argument(
        "--output",
        default="data/output/function_calling_results.json",
    )

    return parser.parse_args()


def main() -> None:
    """Start the program."""
    paths = parse_arguments()

    functions = load_functions(paths.functions_definition)
    prompts = load_prompts(paths.input)

    write_results(paths.output, [])

    try:
        model = Small_LLM_Model(device="cpu")
    except Exception as error:
        sys.exit(f"Error: cannot load the model: {error}")

    vocabulary = get_vocabulary(model)

    names = [function.name for function in functions]

    results: list[dict[str, Any]] = []

    for prompt_item in prompts:
        question = prompt_item.prompt
        text = build_function_prompt(question, functions)
        chosen_name = choose_word(model, vocabulary, text, names)
        chosen_function = find_function(chosen_name, functions)
        parameters = write_all_parameters(
            model, vocabulary, question, chosen_function
        )
        print(question, "->", chosen_name, parameters)

        result = {
            "prompt": question,
            "name": chosen_name,
            "parameters": parameters,
        }
        results.append(result)

    write_results(paths.output, results)
    print("Results written to", paths.output)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("\nStopped by the user (Ctrl+C).")
    except Exception as error:
        sys.exit(f"Error: something went wrong: {error}")

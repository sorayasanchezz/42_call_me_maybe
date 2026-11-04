import json
import sys

from llm_sdk import Small_LLM_Model

from src.function_chooser import choose_word
from src.models import FunctionDefinition
from src.number_writer import write_number
from src.prompt_builder import build_parameters_prompt
from src.string_writer import write_string


def write_value(
    model: Small_LLM_Model,
    vocabulary: list[str],
    prompt_text: str,
    type_name: str,
) -> float | int | bool | str:
    """Let the model write the value of one parameter.

    We choose how to write it by looking at its type.

    Args:
        model: The LLM.
        vocabulary: Text of each token.
        prompt_text: The prompt.
        type_name: The parameter type.

    Returns:
        The value.
    """
    if type_name == "number":
        number_text = write_number(
            model, vocabulary, prompt_text, "0123456789.-"
        )
        return float(number_text)
    elif type_name == "integer":
        number_text = write_number(
            model, vocabulary, prompt_text, "0123456789-"
        )
        return int(number_text)
    elif type_name == "boolean":
        word = choose_word(
            model, vocabulary, prompt_text, ["true", "false"]
        )
        return word == "true"
    elif type_name == "string":
        return write_string(model, vocabulary, prompt_text)
    else:
        sys.exit(f"Error: unknown parameter type: {type_name}")


def write_all_parameters(
    model: Small_LLM_Model,
    vocabulary: list[str],
    question: str,
    function: FunctionDefinition,
) -> dict[str, float | int | bool | str]:
    """Let the model write the value of every parameter of a function.

    We write them one by one. Each written value is added to the text,
    so the model can see it when it writes the next one.

    Args:
        model: The LLM.
        vocabulary: Text of each token.
        question: The user's question.
        function: The chosen function.

    Returns:
        Parameter names and values.
    """
    text = build_parameters_prompt(question, function)

    parameters: dict[str, float | int | bool | str] = {}

    for parameter_name, type_info in function.parameters.items():
        if len(parameters) > 0:
            text += ", "
        text += f'"{parameter_name}": '
        value = write_value(model, vocabulary, text, type_info.type)
        parameters[parameter_name] = value
        text += json.dumps(value)

    return parameters

import json

from src.models import FunctionDefinition


CHOOSE_FUNCTION_RULES = (
    "You choose the function that does what the question asks. "
    "Read the description of every function, then answer with "
    "the name of the best one."
)

WRITE_PARAMETERS_RULES = (
    "You turn a question into a function call in JSON. "
    "Take the values from the question. When a value is described "
    "with words (for example 'any digit' or 'dashes'), write it in "
    "the form the parameter needs: a regular expression for a regex, "
    "the real symbol for a symbol."
)

EXAMPLE_QUESTION = (
    "Question: Send the message 'I said \"see you soon\"' to Maria 3 times\n"
    "Function: fn_send_message\n"
    "Description: Send a text message to a person several times.\n"
    "Parameters: person, message, times"
)

EXAMPLE_ANSWER = json.dumps({
    "name": "fn_send_message",
    "parameters": {
        "person": "Maria",
        "message": 'I said "see you soon"',
        "times": 3,
    },
})


def message(role: str, text: str) -> str:
    """Wrap one chat message in the special tags Qwen understands.

    role is "system" (the rules), "user" (the question)
    or "assistant" (the model's answer).

    Args:
        role: "system", "user" or "assistant".
        text: The message.

    Returns:
        The tagged message.
    """
    return f"<|im_start|>{role}\n{text}<|im_end|>\n"


def start_of_answer() -> str:
    """The beginning of the model's answer.

    The empty <think></think> tells Qwen: "don't think out loud,
    answer directly".

    Returns:
        The start of the answer.
    """
    return "<|im_start|>assistant\n<think>\n\n</think>\n\n"


def build_function_prompt(
    question: str,
    functions: list[FunctionDefinition],
) -> str:
    """Prompt number 1: the model chooses the function.

    We show the list of functions, then the question.
    The text ends with  {"name": "  so the model's next words
    are the function name.

    Args:
        question: The user's question.
        functions: All the functions.

    Returns:
        The prompt, ending with '{"name": "'.
    """
    lines: list[str] = []
    for function in functions:
        parameter_names = ", ".join(function.parameters)
        line = f"- {function.name}({parameter_names}): {function.description}"
        lines.append(line)
    function_list = "\n".join(lines)

    question_text = (
        f"Available functions:\n{function_list}\n\nQuestion: {question}"
    )

    prompt = (
        message("system", CHOOSE_FUNCTION_RULES)
        + message("user", question_text)
        + start_of_answer()
        + '{"name": "'
    )
    return prompt


def build_parameters_prompt(
    question: str,
    function: FunctionDefinition,
) -> str:
    """Prompt number 2: the model writes the parameters.

    The function is already chosen. We show one example first,
    then the real question.
    The text ends with  "parameters": {  so the model's next words
    are the first parameter.

    Args:
        question: The user's question.
        function: The chosen function.

    Returns:
        The prompt, ending with '"parameters": {'.
    """
    parameter_names = ", ".join(function.parameters)
    question_text = (
        f"Question: {question}\n"
        f"Function: {function.name}\n"
        f"Description: {function.description}\n"
        f"Parameters: {parameter_names}"
    )

    prompt = (
        message("system", WRITE_PARAMETERS_RULES)
        + message("user", EXAMPLE_QUESTION)
        + message("assistant", EXAMPLE_ANSWER)
        + message("user", question_text)
        + start_of_answer()
        + '{"name": "' + function.name + '", "parameters": {'
    )
    return prompt

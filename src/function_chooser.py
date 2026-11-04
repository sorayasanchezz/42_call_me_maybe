import sys

from llm_sdk import Small_LLM_Model

from src.models import FunctionDefinition


def get_vocabulary(model: Small_LLM_Model) -> list[str]:
    """Return the text of every token the model knows.

    Position number 5 of the list is the text of token number 5, etc.
    This is slow, so we only do it once.

    Args:
        model: The LLM.

    Returns:
        Token texts; position i is token i.
    """
    token_ids = model.encode("hello")[0].tolist()
    scores = model.get_logits_from_input_ids(token_ids)
    number_of_tokens = len(scores)

    vocabulary: list[str] = []
    for i in range(number_of_tokens):
        vocabulary.append(model.decode([i]))

    return vocabulary


def is_start_of_a_name(text: str, names: list[str]) -> bool:
    """Say if some name of the list starts with this text.

    Example: "fn_ad" is the start of "fn_add_numbers", so True.

    Args:
        text: Start to check.
        names: Possible names.

    Returns:
        True if a name starts with text.
    """
    for name in names:
        if name.startswith(text):
            return True
    return False


def is_end_of_word(text: str) -> bool:
    """Say if this token comes after a finished word in JSON.

    After a function name comes the closing quote: "fn_greet", ...
    After true or false comes "," or "}".

    Args:
        text: The token.

    Returns:
        True if it starts with '"', ',' or '}'.
    """
    if text.startswith('"'):
        return True
    if text.startswith(",") or text.startswith("}"):
        return True
    return False


def words_still_possible(written: str, names: list[str]) -> list[str]:
    """Return the words of the list that start with what is written.

    Example: written = "fn_ad" -> ["fn_add", "fn_add_numbers"]

    Args:
        written: Text written so far.
        names: Possible names.

    Returns:
        The matching names.
    """
    possible: list[str] = []
    for name in names:
        if name.startswith(written):
            possible.append(name)
    return possible


def is_allowed(token_text: str, written: str, names: list[str]) -> bool:
    """Say if the model is allowed to write this token now.

    Two cases are allowed:
    1. The token continues a word of the list ("fn_ad" + "d").
    2. The word is complete and the token closes it ("fn_add" + '"').

    Args:
        token_text: The token.
        written: Text written so far.
        names: Possible names.

    Returns:
        True if it continues or closes a name.
    """
    if token_text == "":
        return False
    if is_start_of_a_name(written + token_text, names):
        return True
    if written in names and is_end_of_word(token_text):
        return True
    return False


def best_allowed_token(
    logits: list[float],
    vocabulary: list[str],
    written: str,
    names: list[str],
) -> int:
    """Return the id of the allowed token with the highest score.

    Args:
        logits: Score of each token.
        vocabulary: Text of each token.
        written: Text written so far.
        names: Possible names.

    Returns:
        The id of the best allowed token.
    """
    best_id = -1
    for i in range(len(vocabulary)):
        if not is_allowed(vocabulary[i], written, names):
            continue
        if best_id == -1 or logits[i] > logits[best_id]:
            best_id = i
    return best_id


def choose_word(
    model: Small_LLM_Model,
    vocabulary: list[str],
    prompt_text: str,
    names: list[str],
) -> str:
    """Let the model write one word of the list, token by token.

    We use it for function names, and for "true" / "false".

    Args:
        model: The LLM.
        vocabulary: Text of each token.
        prompt_text: The prompt.
        names: Possible words.

    Returns:
        The chosen word.
    """
    token_ids = model.encode(prompt_text)[0].tolist()
    written = ""

    while True:
        possible = words_still_possible(written, names)
        if len(possible) == 1:
            return possible[0]

        logits = model.get_logits_from_input_ids(token_ids)
        best_id = best_allowed_token(logits, vocabulary, written, names)
        best_text = vocabulary[best_id]

        if written in names and is_end_of_word(best_text):
            return written

        written += best_text
        token_ids.append(best_id)


def find_function(
    name: str,
    functions: list[FunctionDefinition],
) -> FunctionDefinition:
    """Return the function that has this name.

    Args:
        name: Name to find.
        functions: All the functions.

    Returns:
        The function.
    """
    for function in functions:
        if function.name == name:
            return function

    sys.exit(f"Error: no function called {name}")

import json

from llm_sdk import Small_LLM_Model


def best_string_token(
    logits: list[float],
    vocabulary: list[str],
    is_first: bool,
) -> int:
    """Return the id of the allowed token with the highest score.

    Every token is allowed (except the empty ones), but the
    first one must start with the opening quote.

    Args:
        logits: Score of each token.
        vocabulary: Text of each token.
        is_first: True if it must open the quote.

    Returns:
        The id of the best token.
    """
    best_id = -1
    for i in range(len(vocabulary)):
        token_text = vocabulary[i]
        if token_text == "":
            continue
        if is_first and not token_text.lstrip().startswith('"'):
            continue
        if best_id == -1 or logits[i] > logits[best_id]:
            best_id = i
    return best_id


def text_before_closing_quote(text: str) -> str | None:
    r"""Return the text before the closing quote, or None if not closed.

    A \ always goes in a pair with the next letter: \" is a quote
    inside the text, and \\ is a \. So in 'C:\\"' the last quote
    ends the text.
    Examples: 'hello"' -> 'hello', 'hel' -> None.

    Args:
        text: The text written after the opening quote.

    Returns:
        The text before the closing quote, or None.
    """
    after_backslash = False
    for i in range(len(text)):
        character = text[i]
        if character == '"' and not after_backslash:
            return text[:i]
        if after_backslash:
            after_backslash = False
        elif character == "\\":
            after_backslash = True
    return None


def write_string(
    model: Small_LLM_Model,
    vocabulary: list[str],
    prompt_text: str,
) -> str:
    """Let the model write a text, token by token.

    The prompt must end just before the value, like '"name": '.
    The model writes the opening quote itself, because it usually
    writes it together with the first letters, like ' "/' in "/home".
    We stop when the model writes the closing quote.
    Some letters, like "Ñ", use two tokens, so we always decode
    all the tokens of the text together, never one by one.

    Args:
        model: The LLM.
        vocabulary: Text of each token.
        prompt_text: The prompt.

    Returns:
        The string.
    """
    token_ids = model.encode(prompt_text.rstrip())[0].tolist()
    string_ids: list[int] = []
    written = ""
    max_pieces = 200

    for step in range(max_pieces):
        logits = model.get_logits_from_input_ids(token_ids)
        best_id = best_string_token(logits, vocabulary, step == 0)
        token_ids.append(best_id)
        string_ids.append(best_id)

        text = model.decode(string_ids).lstrip()[1:]
        closed_text = text_before_closing_quote(text)
        if closed_text is not None:
            written = closed_text
            break
        written = text

    try:
        real_text: str = json.loads(f'"{written}"')
        return real_text
    except json.JSONDecodeError:
        return written

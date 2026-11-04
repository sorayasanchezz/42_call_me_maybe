import sys

from llm_sdk import Small_LLM_Model


def is_number_start(text: str, allowed_characters: str) -> bool:
    """Say if this text can be the beginning of a number.

    Examples with "0123456789.-":
    "-", "12" and "3." are True.
    "ab", "1-2" and "1.2.3" are False.

    Args:
        text: Text to check.
        allowed_characters: Characters allowed.

    Returns:
        True if valid so far (one '-' at start, one '.' max).
    """
    for character in text:
        if character not in allowed_characters:
            return False

    if "-" in text[1:]:
        return False

    if text.count(".") > 1:
        return False

    return True


def is_complete_number(text: str) -> bool:
    """Say if this text is already a full number, like "12" or "-3.5".

    "" and "-" are not full numbers yet.

    Args:
        text: Text to check.

    Returns:
        True if float() accepts it.
    """
    try:
        float(text)
        return True
    except ValueError:
        return False


def is_end_of_number(text: str) -> bool:
    """Say if this token ends a number in JSON, like "," or "}".

    Args:
        text: The token.

    Returns:
        True if it starts with ',' or '}'.
    """
    return text.startswith(",") or text.startswith("}")


def write_number(
    model: Small_LLM_Model,
    vocabulary: list[str],
    prompt_text: str,
    allowed_characters: str,
) -> str:
    """Let the model write a number, token by token.

    The model can only pick tokens that keep the text as the start
    of a number. It can only finish ("," or "}") when the number
    is complete, so the result can always be converted.

    Args:
        model: The LLM.
        vocabulary: Text of each token.
        prompt_text: The prompt.
        allowed_characters: Characters allowed.

    Returns:
        The number as text.
    """
    token_ids = model.encode(prompt_text.rstrip())[0].tolist()
    written = ""
    max_pieces = 100

    for step in range(max_pieces):
        logits = model.get_logits_from_input_ids(token_ids)

        best_id = -1
        for i in range(len(vocabulary)):
            token_text = vocabulary[i]
            if token_text == "":
                continue
            if step == 0:
                token_text = token_text.lstrip(" ")
            can_continue = is_number_start(
                written + token_text, allowed_characters
            )
            can_finish = (
                is_end_of_number(token_text)
                and is_complete_number(written)
            )
            if not can_continue and not can_finish:
                continue
            if best_id == -1 or logits[i] > logits[best_id]:
                best_id = i

        best_text = vocabulary[best_id]
        if step == 0:
            best_text = best_text.lstrip(" ")

        if is_end_of_number(best_text):
            break

        written += best_text
        token_ids.append(best_id)

    if not is_complete_number(written):
        sys.exit(f"Error: the model could not write a number: {written}")

    return written

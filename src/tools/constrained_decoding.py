from src.tools.models import Function_definition
from llm_sdk import Small_LLM_Model  # type: ignore
import json
from typing import Any


def extract_valid_json(text: str) -> Any:
    '''
    Checks if the text contains a valid json.
    Arg:
        text: the string generated previously.
    Return:
        the valid json if the text contains it, else None.
    '''
    start = text.find("{")
    if start == -1:
        return None
    bracket_count = 0
    for loc in range(start, len(text)):
        if text[loc] == "{":
            bracket_count += 1
        if text[loc] == "}":
            bracket_count -= 1
        if bracket_count == 0:
            return text[start:loc + 1]
    return None


def get_the_best_id(valid_ids: set[int], logits: list[float]) -> int:
    '''
    Find the valid id having highest logit among valid_ids.
    Args:
        valid_ids: set of ids which correspond to tokens that can be
                    put in the output to get a valid json.
        logits: list of the logits.
    Return:
        return the best id(the one having the highest logit among
        valid_ids)
    '''
    return max(valid_ids, key=lambda i: logits[i])


def filter_json_valid_ids(vocabulary: dict[str, int]) -> set[int]:
    '''
    Filter the vocabulary in order to only get the ids which correspond
    to tokens that can be put in the output to get a valid json.
    Arg:
        vocabulary loaded from the path given by the model.
    Return:
        set of ids corresponding to tokens that can be put in the output
        to get a valid json.
    '''
    safe_char = set(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        '0123456789*_.,:-+/\'!?()[]{}"ĠĊ'
    )
    valid_ids = set()
    for token_str, token_id in vocabulary.items():
        if token_str and all(c in safe_char for c in token_str):
            valid_ids.add(token_id)
    return valid_ids


def load_vocabulary(model: Small_LLM_Model) -> Any:
    '''
    Get the path from the model and load the model's vocabulary from that
    path.
    Arg:
        model.
    return:
        the model's vocabulary.
    '''
    path_to_vocab = model.get_path_to_vocab_file()
    with open(path_to_vocab) as file:
        raw_vocab = json.load(file)
    return raw_vocab


def build_system_prompt(functions: list[Function_definition]) -> str:
    '''
    Return a pre-prompt containing clear instructions to the model.
    Arg:
        functions: list of the functions' definitions from input files.
    Return:
        the pre-prompt
    '''
    rule = "the user's intent (even if types match), set name: \"none\"."
    lines = [
        "STRICT SYSTEM RULE: Use ONLY a matching function from the list below",
        f"If NO function matches {rule}",
        "Never use an unrelated function for a different task.",
        "",
        "Available functions:"
    ]
    for fn in functions:
        params = ", ".join(
            f"{name} : {info.type}" for name, info in fn.parameters.items()
        )
        lines.append(f" -{fn.name}({params}): {fn.description}")

    lines.append(
        '\nOutput ONLY valid JSON:{"name" : "<fn>", "arguments": {<argument>}}'
        )
    return "\n".join(lines)

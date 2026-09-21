from src.tools.models import Function_definition
from llm_sdk import Small_LLM_Model  # type: ignore
import json


def chose_between(names: list[str], model: Small_LLM_Model, all_ids: list[int]):
    identifiers = "abcdefghijklmnopqrstuvwxyz"
    identifiers = identifiers[0:len(names)]
    valid_ids = []
    for identifier in identifiers:
        valid_ids += [(model.encode(identifier)[0])]
    logits = model.get_logits_from_input_ids(all_ids)
    chosen_name_nb = get_the_best_id(valid_ids, logits)
    loc = identifiers.find(model.decode(chosen_name_nb))
    return names[loc]

def chose_name(
        names: list[str], model: Small_LLM_Model, all_ids: list[int]
        ) -> str:
    name = chose_between(names, model, all_ids) + '"'
    print(name, end="")
    return name


def get_parameters_ids(
        func: Function_definition, model: Small_LLM_Model, all_ids: list[int]
        ) -> str:

    path_to_vocab = model.get_path_to_vocab_file()
    with open(path_to_vocab, "r", encoding='utf-8') as f:
        vocab = json.load(f)

    safe_number_ids = [
        id for token, id in vocab.items() if (
            token and all(c in '0123456789".' for c in token)
            )
        ]
    safe_char = set(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        '0123456789*_.,:-+/\\\'!?()[]{}"ĠĊ'
    )
    safe_string_ids = [
        id for token, id in vocab.items() if (
            token and all(c in safe_char for c in token)
            )
        ]
    safe_bool_ids = [
        id for token, id in vocab.items() if (
            token and all(c in 'true"false' for c in token)
            )
        ]
    
    res_id = []
    for parameter in func.parameters:
        print(f'"{parameter}":"', end="", flush=True)
        param = '"' + parameter + '":"'
        res_id.extend(model.encode(param)[0].tolist())
        if func.parameters[parameter].type in ['number', 'integer']:
            valid_ids = safe_number_ids
        elif func.parameters[parameter].type == "string":
            valid_ids = safe_string_ids
        elif func.parameters[parameter].type == "boolean":
            valid_ids = safe_bool_ids
        chosen_text = ""
        all_chosen_text = ""
        token_nb = 0
        while '"' not in chosen_text:
            logits = model.get_logits_from_input_ids(all_ids + res_id)
            chosen_id = get_the_best_id(valid_ids, logits)
            chosen_text = model.decode([chosen_id])
            if len(all_chosen_text) > 10 and all_chosen_text[(len(all_chosen_text) - 10):] in all_chosen_text[0:(len(all_chosen_text) - 10)] or token_nb > 50:
                chosen_text = '"'
                chosen_id = model.encode('"')[0].tolist()[0]
            if '"' in chosen_text and chosen_text != '"':
                chosen_text = chosen_text[0:(chosen_text.find('"') + 1)]
                chosen_id = model.encode(chosen_text)[0].tolist()
                res_id.extend(chosen_id)
            else:
                res_id.append(chosen_id)
            print(chosen_text, end="", flush=True)
            all_chosen_text += chosen_text
            token_nb += 1

        if parameter != list(func.parameters.keys())[len(func.parameters) - 1]:
            res_id.extend(model.encode(',')[0].tolist())
            print(",", end="", flush=True)
    res_id.extend(model.encode('}')[0].tolist())
    print("}", end="", flush=True)
    return res_id



def generate_next_tokens(
        state: str, model: Small_LLM_Model, name: str,
        all_ids: list[int], funcs: list[Function_definition]) -> list[int]:

    tokens = []
    if state == "NAME":
        func_names = [func.name for func in funcs]
        func_name = chose_name(func_names, model, all_ids)
        tokens.extend(model.encode(func_name)[0].tolist())
    elif state == "PARAMETERS_KEY":
        print(',"parameters":{', end="", flush=True)
        tokens.extend(model.encode(',"parameters":{')[0].tolist())
    elif state == "PARAMETERS":
        name = name[0:(len(name) - 1)]
        func = next(filter(lambda x: x.name == name, funcs), None)
        if not func or len(func.parameters) == 0:
            print('}', end="", flush=True)
            tokens.extend(model.encode('}')[0].tolist())
        else:
            tokens.extend(get_parameters_ids(func, model, all_ids))
    elif state == "AFTER_PARAMETERS":
        print('}', end="", flush=True)
        tokens.extend(model.encode('}')[0].tolist())
    return tokens


def get_the_best_id(valid_ids: set[int], logits: list[float]) -> int:
    '''
    Find the valid id having highest logit among valid_ids.
    Args:
        valid_ids: list of ids which correspond to tokens that can be
                    put in the output to get a valid json.
        logits: list of the logits.
    Return:
        return an int of the id having the highest logit among valid_ids
    '''
    return max(valid_ids, key=lambda i: logits[i])


def build_system_prompt(functions: list[Function_definition]) -> str:
    '''
    Return a pre-prompt containing clear instructions to the model.
    Arg:
        functions: list of the functions' definitions from input files.
    Return:
        the pre-prompt
    '''
    identifiers = "abcdefghijklmnopqrstuvwxyz"
    lines = [
        "STRICT SYSTEM RULE: Use ONLY a matching function from the list below",
        "Never use an unrelated function for a different task.",
        "",
        "Available functions:"
    ]
    loc = 0
    for fn in functions:
        params = ", ".join(
            f"{name} : {info.type}" for name, info in fn.parameters.items()
        )
        lines.append(f" -{identifiers[loc]}({params}): {fn.description}")
        loc += 1
    a = 'Output ONLY valid JSON:{"name" : "<fn>", "parameters": {<argument>}}'
    lines.append("\n" + a)
    return "\n".join(lines)

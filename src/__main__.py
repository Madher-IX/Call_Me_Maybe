from src.tools.parse_arg import parse_arg
from src.tools.load_json_file import load_inputs
from src.tools.constrained_decoding import build_system_prompt, generate_next_tokens
from llm_sdk import Small_LLM_Model  # type: ignore
import time
from typing import Any
from src.tools.models import Function_definition
from src.tools.cast_output import cast_output
import json
import os
#check if dependencies are all intalled first.


def double_anti_slash(text: str) -> str:
    '''
    Double anti-slashes in the text so json can load it without error.
    Arg:
        the text
    Return:
        the result
    '''
    result = ""
    for char in text:
        result += char
        if char == "\\":
            result += "\\"
    return result


def get_next_state(state: str) -> str:
    states = {
        "NAME": "PARAMETERS_KEY",
        "PARAMETERS_KEY": "PARAMETERS",
        "PARAMETERS": "AFTER_PARAMETERS",
        "AFTER_PARAMETERS": "DONE"
    }
    return states[state]


def process_prompt(
        model: Small_LLM_Model, full_prompt: str,
        funcs: list[Function_definition], prompt: str
        ) -> dict[str, Any]:
    
    input_ids = model.encode(full_prompt)[0].tolist()
    generated_token_ids = []
    generated_token_ids.extend(model.encode('{"name":"')[0].tolist())
    print('\t⟶ {"name":"', end="", flush=True)

    state = "NAME"
    name = ""

    while state != "DONE":
        #list of the id of generated tokens.
        all_ids = input_ids + generated_token_ids
        to_add = generate_next_tokens(state, model, name, all_ids, funcs)
        if state == "NAME":
            name = model.decode(to_add)
        generated_token_ids.extend(to_add)
        state = get_next_state(state)

    try:
        generated_text = model.decode(generated_token_ids)
        if '\\' in generated_text:
            generated_text = double_anti_slash(generated_text)
        generated_json = json.loads(generated_text)
    except json.JSONDecodeError as error:
        print(error)
        pass

    return {
        "prompt": prompt,
        "name": generated_json.get("name" ,"none"),
        "parameters": generated_json.get("parameters", {})
    }


def main() -> None:

    print("Call me maybe\n\n")
    args = parse_arg()

    print("[Loading:]")
    print(f"\t-Prompts from {args.input}")
    print(f"\t-Functions definition from {args.functions_definition}")
    prompts, funcs_def = load_inputs(args)

    system_prompt = build_system_prompt(funcs_def)

    print("\n\nInstanciating the model...")
    try:
        model = Small_LLM_Model()
    except OSError:
        raise RuntimeError(
            "The model is not available."
        )

    print("\n\n[START]")
    start_time = time.time()

    all_results: list[dict[str, Any]] = []

    for p in prompts:
        print(f"\n\n[#] Processing the prompt: {p.prompt!r}...")
        if p.prompt in [res["prompt"] for res in all_results]:
            print("The prompt have already been processed before.")
            result = next(filter(lambda x: x["prompt"]==p.prompt, all_results))
        else:
            full = f"{system_prompt}\n\nUser prompt: {p.prompt}\nAssistant:"
            result = process_prompt(model, full, funcs_def, p.prompt)
        all_results.append(result)

    print("\n\n[END]")
    total_time = time.time() - start_time
    print(f"Total time: {round(total_time, 2)} seconds.")
    casted_results = [cast_output(obj, funcs_def) for obj in all_results]

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as output_file:
        json.dump(casted_results, output_file, ensure_ascii=False, indent=2)
    print(f"\nResults are saved in {args.output!r}.")

if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(error)
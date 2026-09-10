from src.tools.parse_arg import parse_arg
from src.tools.load_json_file import load_prompt, load_function_definition
try:
    from src.tools.constrained_decoding import build_system_prompt
    from src.tools.constrained_decoding import load_vocabulary
    from src.tools.constrained_decoding import filter_json_valid_ids
    from src.tools.constrained_decoding import get_the_best_id
    from src.tools.constrained_decoding import extract_valid_json
    from llm_sdk import Small_LLM_Model  # type: ignore
except (KeyboardInterrupt, ImportError, ModuleNotFoundError, RuntimeError):
    print("\nThe User stopped the program.")
import time
import json
import os


def main() -> None:
    '''
    The main pipeline, loads everything, processes prompts
    and generates outputs token-by-token and saves output.
    Arg:
        takes nothing
    Return:
        return nothing
    '''
    call_me_maybe = r"""
 ██████╗ █████╗ ██╗     ██╗
██╔════╝██╔══██╗██║     ██║
██║     ███████║██║     ██║
██║     ██╔══██║██║     ██║
╚██████╗██║  ██║███████╗███████╗
 ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝

███╗   ███╗███████╗
████╗ ████║██╔════╝
██╔████╔██║█████╗
██║╚██╔╝██║██╔══╝
██║ ╚═╝ ██║███████╗
╚═╝     ╚═╝╚══════╝

███╗   ███╗ █████╗ ██╗   ██╗██████╗ ███████╗
████╗ ████║██╔══██╗╚██╗ ██╔╝██╔══██╗██╔════╝
██╔████╔██║███████║ ╚████╔╝ ██████╔╝█████╗
██║╚██╔╝██║██╔══██║  ╚██╔╝  ██╔══██╗██╔══╝
██║ ╚═╝ ██║██║  ██║   ██║   ██████╔╝███████╗
╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═════╝ ╚══════╝
"""
    for c in call_me_maybe:
        print(c, end="")
    print("\n\n⚡Starting...")
    paths = parse_arg()

    print("\tLoading prompts and functions...")
    prompts = load_prompt(paths.input)
    if not prompts:
        raise RuntimeError(
            "No prompt found, Please provide at least 1 prompt."
            )
    func_defs = load_function_definition(paths.function_definition)
    if not func_defs:
        raise RuntimeError(
            "No function found, Please provide at least 1 function."
            )

    print("\tBuilding system prompt...")
    system_prompt = build_system_prompt(func_defs)

    print("\tLoading the Model ...")
    try:
        model = Small_LLM_Model()
    except OSError:
        raise RuntimeError(
            "The model is not available."
        )
    print("\tFiltering json valid ids...\n\n")
    vocabulary = load_vocabulary(model)
    valid_ids = filter_json_valid_ids(vocabulary)

    start_time = time.time()
    all_results = []
    for p in prompts:
        prompt = p.prompt
        print(f"\n⏳ Processing prompt: {prompt!r}...\n\t⟶ ", end="")
        full_prompt = f"{system_prompt}\n\nUser prompt: {prompt}\nAssistant:"
        input_ids = model.encode(full_prompt)[0].tolist()

        all_generated_token_ids = []
        all_generated_token_ids.extend(model.encode('{"name":"')[0].tolist())
        print('{"name":"', end="")

        clean_json = None
        parsed = {"name": "none", "arguments": {}}
        while not clean_json:
            logits = model.get_logits_from_input_ids(
                input_ids + all_generated_token_ids
                )
            next_id = get_the_best_id(valid_ids, logits)
            print(model.decode([next_id]), end="", flush=True)
            all_generated_token_ids.append(next_id)
            text = model.decode(all_generated_token_ids)

            clean_json = extract_valid_json(text)

        parsed = json.loads(clean_json)
        all_results.append(
            {
                "prompt": prompt,
                "name": parsed.get("name", "none"),
                "arguments": parsed.get("arguments", {})
            }
        )
        if parsed.get("name", "none") != "none":
            print("\n\t[✅]The prompt is successfully processed:")
            print(f"\t->{parsed.get("name")}:{parsed.get("arguments")}")
        if parsed.get("name", "none") == "none":
            print("\n\t[❌]: Something went wrong during the process")
            print(
                "\tPlease, Make sure your prompt can match with one ", end=""
                )
            print("of the provided function definition.")

    total_time = time.time() - start_time
    parsed_results = [res for res in all_results if res.get("name") != "none"]
    os.makedirs(os.path.dirname(paths.output), exist_ok=True)
    with open(paths.output, "w", encoding="utf-8") as output_file:
        json.dump(parsed_results, output_file, ensure_ascii=False, indent=2)
    print(f"\n\n\n[💾]The results are saved in :{paths.output!r}.")
    print(f"[⌛]Total time: {round(total_time, 2)} seconds.")
    print("[📊]Number of prompt successfully processed: ", end="")
    print(f"{len(parsed_results)}/{len(all_results)}.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nThe User stopped the program.")
    except Exception as error:
        print(f"Error: {error}")

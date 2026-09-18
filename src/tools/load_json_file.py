import json
from .models import Prompt, Function_definition
from pydantic import ValidationError
from argparse import Namespace
from typing import Any



def load_inputs(
        args: Namespace
        ) -> tuple[list[Prompt], list[Function_definition]]:
    prompts = load_prompt(args.input)
    funcs_def = load_function_definition(args.functions_definition)
    if 0 in [len(prompts), len(funcs_def)]:
        raise RuntimeError(
            "Please provide at least one prompt and one function definition."
        )
    func_names = [func.name for func in funcs_def]
    if len(func_names) != len(set(func_names)):
        raise RuntimeError(
            "Please, make sure that each function have their own name."
        )
    return(prompts, funcs_def)


def load_prompt(path: str) -> list[Prompt]:
    '''
    loads prompts from the input file.
    arg:
        path: path to the provided input file.
    return:
        list of prompts.
    '''
    try:
        with open(path, "r", encoding="utf-8") as file:
            prompts = json.load(file)
        return [Prompt(**prompt) for prompt in prompts]
    except FileNotFoundError:
        raise RuntimeError(f"The file {path} was not found.")
    except json.JSONDecodeError:
        error = "The json file contains a wrong format."
        raise RuntimeError(error)
    except Exception as error:
        raise RuntimeError(f"Unexpected error: {error}")


def load_function_definition(path: str) -> list[Function_definition]:
    '''
    loads function definitions from input file.
    arg:
        path: path to the provided input file.
    return:
        list of function definitions.
    '''
    try:
        with open(path, "r", encoding="utf-8") as file:
            func_defs = json.load(file)
        return [Function_definition(**func_def) for func_def in func_defs]
    except FileNotFoundError:
        raise RuntimeError(f"The file {path} was not found.")
    except json.JSONDecodeError:
        error = "The json file contains a wrong format."
        raise RuntimeError(error)
    except Exception as error:
        raise RuntimeError(f"Unexpected error: {error}")
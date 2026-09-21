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
    if len(funcs_def) > 26:
        raise RuntimeError(
            "Please provide less than 27 function definitions."
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
    except FileNotFoundError:
        raise RuntimeError(f"The file {path} was not found.")
    except json.JSONDecodeError:
        raise RuntimeError("The json file contains a wrong format.")

    if not isinstance(prompts, list):
        raise RuntimeError("The input JSON must be a list of prompt objects.")

    try:
        return [Prompt(**prompt) for prompt in prompts]
    except ValidationError as error:
        raise RuntimeError(f"Invalid prompt data: {error.errors()[0]['msg']}") from error
    except Exception as error:
        raise RuntimeError(f"Unexpected error while reading prompts: {error}") from error


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
    except FileNotFoundError:
        raise RuntimeError(f"The file {path} was not found.")
    except json.JSONDecodeError:
        raise RuntimeError("The json file contains a wrong format.")

    if not isinstance(func_defs, list):
        raise RuntimeError(
            "The functions definition JSON must be a JSON array of function definitions."
        )

    try:
        return [Function_definition(**func_def) for func_def in func_defs]
    except ValidationError as error:
        raise RuntimeError(
            f"Invalid function definition: {error.errors()[0]['msg']}"
        ) from error
    except Exception as error:
        raise RuntimeError(f"Unexpected error while reading function definitions: {error}") from error
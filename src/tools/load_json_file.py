import json
from .models import Prompt, Function_definition
from pydantic import ValidationError


def load_prompt(path: str) -> list[Prompt]:
    try:
        with open(path, "r", encoding="utf-8") as file:
            prompts = json.load(file)
        return [Prompt(**prompt) for prompt in prompts]
    except FileNotFoundError:
        raise RuntimeError(f"The file {path} was not found.")
    except json.JSONDecodeError:
        error = "The json file contains a wrong format."
        raise RuntimeError(error)
    except ValidationError:
        raise RuntimeError("invalid prompt.")


def load_function_definition(path: str) -> list[Function_definition]:
    try:
        with open(path, "r", encoding="utf-8") as file:
            func_defs = json.load(file)
        return [Function_definition(**func_def) for func_def in func_defs]
    except FileNotFoundError:
        raise RuntimeError(f"The file {path} was not found.")
    except json.JSONDecodeError:
        error = "The json file contains a wrong format."
        raise RuntimeError(error)
    except ValidationError:
        raise RuntimeError("invalid function definition.")

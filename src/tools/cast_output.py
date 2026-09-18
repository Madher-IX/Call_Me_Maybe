from typing import Any
from .models import Function_definition


def cast_output(
        object: dict[str, Any], functions: list[Function_definition]
        ) -> dict[str, Any]:
    funcs = {func.name: func for func in functions}

    res_object: dict[str, Any] = {
        "prompt": object["prompt"],
        "name": object["name"],
        "parameters": object["parameters"]
    }

    for parameter in res_object["parameters"]:
        param_type = funcs[res_object["name"]].parameters[parameter].type
        res_object_param = res_object["parameters"][parameter]
        if param_type == "number":
            if res_object_param == "":
                param = 0.0 + 0.0
            else:
                param = float(res_object_param) + 0.0
            res_object["parameters"][parameter] = param
        elif param_type == "integer":
            if res_object_param == "":
                res_object_param = 0
            res_object["parameters"][parameter] = int(res_object_param)
        elif param_type == "string":
            res_object["parameters"][parameter] = str(res_object_param)
        elif param_type == "boolean":
            val = res_object_param
            if isinstance(val, str):
                if val.lower() == "false":
                    res_object["parameters"][parameter] = False
                elif val.lower() == "true":
                    res_object["parameters"][parameter] = True
            else:
                ans = bool(res_object_param)
                res_object["parameters"][parameter] = ans
    return res_object

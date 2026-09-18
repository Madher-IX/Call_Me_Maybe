from pydantic import BaseModel, model_validator, ConfigDict
import numpy as np


class Prompt(BaseModel):
    '''
    -Contains the data of a given prompt.
    -This class helps with input's validation
    when loading input file.
    '''
    prompt: str
    model_config = ConfigDict(extra="forbid")


class Parameter(BaseModel):
    '''
    the function definition's parameter.
    '''
    type: str
    model_config = ConfigDict(extra="forbid")


class Return(BaseModel):
    '''
    the function definition's return.
    '''
    type: str
    model_config = ConfigDict(extra="forbid")


class Function_definition(BaseModel):
    '''
    -Contains the data of a given function definition.
    -This class helps with input's validation when
    loading input file.
    '''
    name: str
    description: str
    parameters: dict[str, Parameter]
    returns: Return
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode='after')
    def check_type(self) -> "Function_definition":
        allowed_types = ["number", "integer", "boolean", "string"]
        if not self.name or not self.name.isidentifier():
            msg = "is not a valid Python identifier/function name."
            raise ValueError(
                f"'{self.name}' {msg}"
            )
        for parameter in self.parameters:
            if self.parameters[parameter].type.lower() not in allowed_types:
                msg1 = "Invalid type of parameter for the definition "
                msg2 = f"of the function {self.name}.\nValid types are: "
                msg3 = "number, integer, string, boolean."
                raise ValueError(
                    f"{msg1}{msg2}{msg3}"
                    )
        return self

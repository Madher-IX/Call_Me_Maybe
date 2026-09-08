from pydantic import BaseModel


class Prompt(BaseModel):
    prompt: str


class Parameter(BaseModel):
    type: str


class Return(BaseModel):
    type: str


class Function_definition(BaseModel):
    name: str
    description: str
    parameters: dict[str, Parameter]
    returns: Return

from pydantic import BaseModel


class Prompt(BaseModel):
    '''
    -Contains the data of a given prompt.
    -This class helps with input's validation
    when loading input file.
    '''
    prompt: str


class Parameter(BaseModel):
    '''
    the function definition's parameter.
    '''
    type: str


class Return(BaseModel):
    '''
    the function definition's return.
    '''
    type: str


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

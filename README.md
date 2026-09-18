 *This project has been created as part of the 42 curriculum by tsiarran.*


# Description
The project Call_Me_Maybe consists of creating a function calling, a kind of tool that helps models to produce structured, machine-executable output by translating natural language prompts into structured function calls.

The project's goal is to introduce us to function calling in Large Language Models.

So in this project, with the given model (Qwen/Qwen3-0.6B), prompt from the input files will be processed in order to produce a json object containing the name of one of the functions in the functions_definitions file with the corresponding arguments which can help to answer the prompt.
The model will be guided by our program token-by-token (with the constrained decoding) so we surely get a valid json with the required schema.All valid jsons will be written in the output file.

# Instructions
Firstly, it is necessary to make sure that there is enough space for the dependencies(including the model).

Then run:

- `make install` : to install all the dependencies(it actually uses `uv sync`).
- `make run` : to execute the main script (with `uv run python -m src`).
- `make clean` : to remove temporary files.
- `make fclean` : to remove all directories created in the "goinfre".
- `make debug` : to run the main script in debug mode using python’s built-in debugger.
- `make lint` : to run `flake8 .` and `mypy .` .

`GOOD TO KNOW`: Since all the cache of the uv and hugging face are redirected by make install in goinfre, it is better and easier to just add the flags in Makefile when testing if the program works with:
`uv run python -m src [--functions_definition <function_definition_file>] [--input <input_file>] [--output <output_file>]`

# Resources
- `peer learning`: discuss with peers.
- `youtube      `: tutorials and some hints about how token generation really works.

## AI usage
- for translation:to understand the subject's requirements.

# Algorithm explanation and design decisions
When asking something to somebody, it is always judged better to be clear with the assignment from the start; The same applies to Model, so:


- `in first`: a pre-prompt is given to the model with the prompt, the pre-prompt are some clear instructions about the model to only generate one of the listed functions in the provided function definitions, and that the only valid output is the json schema: `{"name" : "<fn>", "parameters": {<argument>}}`.

- Therefore, the program is far from just depending on that pre-prompt:

- `constrained decoding` : after calculating the logits, instead of putting all invalid token's logit to float("-inf"), the program only takes into account the json valid tokens, tokens that contain only safe json characters as: `abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ` and `0123456789*_.,:-+/\'!?()[]{}"ĠĊ`, and it just chooses the one having the highest logit among them.

- `Then how to be sure that the output will be 100% json valid?`:
At the very start, just before the generation of token-by-token, the program guides the model to generate the json schema: `{"name" : "<fn>", "parameters": {<argument>}}` by giving it the first part of it `{"name" : "`.And since the pre-prompt is already showing the model the right schema, it follows automatically the schema.

### The pipeline:
   - 1 -> encode the pre-prompt + prompt  => We get ids from this encoding.
   - 2 -> get logits from the previous ids + the generated tokens'ids(generated_tokens have no element at the very start except the `{"name":"`'s token).
   - 3 -> get the id of the token having the highest logit among the valid ones.
   - 4 -> add the chosen id to the generated tokens'ids.
   - 2-3-4 is repeated in a loop until a valid json is generated.
   - check if the valid json correspond to the function definition.


# Performance analysis
- The Ouput is a valid json.

- The speed and accuracy depends on the prompt and the function definitions.

- The solution is pretty reliable.

# Challenges faced
- Understanding the assignement, it took several times to understand...The only way to solve that was constancy, keeping reading the subject, asking the other students and trying to use some of the provided tools.

# Example usage && Testing strategy
- tried to run the program with invalid inputs and put some prompts that have nothing to do with the function definitions, nothing went wrong, and the program works correctly with valid input like the example below,and meets the subject's requirements so I think that the implementation is valid.

## Simple Example of usage:
- At the root of the project, run:
`make install`

- Then, once all dependencies are downloaded, run:
`make run`

- Wait the generation ...

- once the generation done, results will be saved to the output file.

## Testing flags:
- To check if the flags `--input`, `--output`, `--function_definition`, it is easier to check it by just modifying the option `run` in `Makefile` than trying to run `uv run python -m src --...` on the command line because of the adjustment done due to the small space we have on our computer in our campus.

- But if you really need to execute the main script on the command line, then run:
`HF_HOME=path_to_your_goinfre/call_me_maybe_cache/huggingface UV_CACHE_DIR=path_to_your_goinfre/call_me_maybe_cache/uv UV_PROJECT_ENVIRONMENT=path_to_your_goinfre/call_me_maybe_venv uv run python -m src --<FLAG> "<ARG>"`
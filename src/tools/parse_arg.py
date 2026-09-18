import argparse


def parse_arg() -> argparse.Namespace:
    '''
    Adds the inputs and output flag so we can add arguments
    at the command line.
    Arg:
        It takes nothing.
    Return:
        An (argparse.Namespace) object having attributes:
        ->input, function_definition, output.
    '''
    desc = "translate natural language prompts into structured function call"
    parser = argparse.ArgumentParser(
        description=desc
    )
    parser.add_argument(
        "--input",
        type=str,
        default="data/input/function_calling_tests.json"
    )
    parser.add_argument(
        "--functions_definition",
        type=str,
        default="data/input/functions_definition.json"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/output/function_calling_results.json"
    )
    return parser.parse_args()

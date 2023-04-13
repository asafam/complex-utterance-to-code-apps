import argparse
import glob
import os
from pathlib import Path
import pandas as pd
from enum import Enum


class States(Enum):
    IMPORTS = "imports"
    DOCSTRING = "docstring"
    TEST = "test"
    CODE = "code"


def get_input_file_paths(input_file_path_regexp: str):
    """
    Get input file paths.

    params:
    input_file_path_regexp: str. Regular expression for input file paths.

    returns:
    input_file_paths: list. List of input file paths.
    """
    input_file_paths = glob.glob(input_file_path_regexp)
    return input_file_paths


def read_data(
    input_file_path: str,
    docstring_prefix: str = '"""',
    docstring_suffix: str = '"""',
    id_prefix: str = "def test_",
    id_suffix: str = "():\n",
    code_block_start_str: str = "# start code block to test",
    code_block_end_str: str = "# end code block to test",
):
    """
    Read data from input file and parse it into a list of id, text and code dictionaries.
    The text and code values are enclosed in python function definitions.
    Text is expcted to be enclosed in triple quotes docstrings. A test is expected to
    follow the docstring.

    params:
    input_file_path: str. Input file path.

    returns:
    A list of id, text and test dictionaries.
    """
    with open(input_file_path, "r") as input_file:
        data = []
        id = None
        imports = None
        text = None
        code = None
        test = None
        leading_spaces = 0

        state = None
        for line in input_file:
            if line.startswith(id_prefix):
                if id and text and test:
                    item = next(
                        (item for item in data if id and item["id"] == id), None
                    )
                    if not item:
                        item = {
                            "id": id,
                            "text": text,
                            "code": code,
                            "test": test,
                            "imports": imports,
                        }
                        data.append(item)
                    else:
                        item[f"code_{len(item.keys()) - 3 + 1}"] = test

                state = States.TEST
                leading_spaces = len(line) - len(line.lstrip()) + 4
                id = str(line[len(id_prefix) : -len(id_suffix)].strip().split("_")[0])
                text = None
                test = None
                code = None

            elif state == States.DOCSTRING:
                if line.strip().startswith(docstring_prefix):
                    state = States.TEST
                else:
                    text = line.strip() if text is None else f"{text} {line.strip()}"

            elif state == States.TEST:
                if line.strip().startswith(docstring_suffix):
                    state = States.DOCSTRING  # start code block to test
                else:
                    if line.strip().startswith(code_block_start_str):
                        state = States.CODE
                    test = add_line_to_var(test, line, leading_spaces=leading_spaces)

            elif state == States.CODE:
                if line.strip().startswith(code_block_end_str):
                    state = States.TEST
                    test = add_line_to_var(test, line, leading_spaces=leading_spaces)
                else:
                    code = add_line_to_var(code, line, leading_spaces=leading_spaces)

            if line.strip().startswith("import") or line.strip().startswith("from"):
                state = States.IMPORTS
                imports = add_line_to_var(imports, line, leading_spaces=leading_spaces)

        return data


def add_line_to_var(var, line, leading_spaces=0):
    if var is None:
        var = line[leading_spaces:]
    else:
        var += line[leading_spaces:] if line.strip() != "" else line
    return var


def write_data(data: list, output_file: str):
    df = pd.DataFrame(data)  # Convert data to dataframe
    base_path = os.path.dirname(os.path.abspath(output_file))  # Get base path
    Path(base_path).mkdir(
        parents=True, exist_ok=True
    )  # Create directory if it doesn't exist
    df.to_csv(output_file, index=False, compression="gzip")  # Write data to file


def main(input_file_path_regexp: str, output_file: str):
    """
    Main function.

    params:
    input_file_path_regexp: str. Regular expression for input file paths.
    output_file: str. Output file path.
    """
    input_file_paths = get_input_file_paths(input_file_path_regexp)

    data = []
    for input_file_path in input_file_paths:
        data += read_data(input_file_path)

    write_data(data, output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="API Files Ingestor")
    parser.add_argument(
        "--input_file_path_regexp", type=str, help="Input file path regexp"
    )
    parser.add_argument("--output_file", type=str, help="Output file path")

    main(**vars(parser.parse_args()))

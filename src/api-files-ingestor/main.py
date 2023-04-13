import argparse
import glob
import os
from pathlib import Path
import pandas as pd


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
    input_file_path: str, id_prefix: str = "def test_", id_suffix: str = "():\n"
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
    states = {
        "in function": "in function",
        "in docstring": "in docstring",
        "in code": "in code",
        "out of function": "out of function",
    }
    with open(input_file_path, "r") as input_file:
        data = []
        id = None
        text = None
        test = None
        state = states.get("out of function")
        for line in input_file:
            if line.startswith(id_prefix):
                if id and text and test:
                    item = next(
                        (item for item in data if id and item["id"] == id), None
                    )
                    if not item:
                        item = {"id": id, "text": text, "test": test}
                        data.append(item)
                    else:
                        item[f"code_{len(item.keys()) - 3 + 1}"] = test

                state = states.get("in function")
                id = str(line[len(id_prefix) : -len(id_suffix)].strip().split("_")[0])
                text = None
                test = None

            elif line.strip().startswith('"""') and state == states.get("in function"):
                state = states.get("in docstring")
            elif line.strip().startswith('"""') and state == states.get("in docstring"):
                state = states.get("in code")
            elif state == states.get("in docstring"):
                if text is None:
                    text = line.strip()
                else:
                    text += f" {line}"
            elif state == states.get("in code"):
                if test is None:
                    leading_spaces = len(line) - len(line.lstrip())
                    test = line[leading_spaces:]
                else:
                    test += line[leading_spaces:] if line.strip() != "" else line

        return data


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

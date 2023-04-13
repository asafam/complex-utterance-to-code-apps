

def execute_program(program_str: str):
    try:
        exec(program_str)
    except AssertionError as e:
        
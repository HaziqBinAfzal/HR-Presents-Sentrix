import ast


def check_syntax(file_path):
    """
    Check Python syntax.
    """

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            ast.parse(file.read())

        return {
            "valid": True,
            "line": None,
            "message": ""
        }

    except SyntaxError as error:

        return {

            "valid": False,

            "line": error.lineno,

            "message": error.msg

        }

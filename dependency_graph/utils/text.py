def _slice_text_around(
    text: str, start_line: int, start_column: int, end_line: int, end_column: int
) -> tuple[str, str]:
    """
    Slice the text around the specified portion of the text.
    :param text: The text to slice
    :param start_line: The line number of the start of the desired portion of the text
    :param start_column: The column number of the start of the desired portion of the text
    :param end_line: The line number of the end of the desired portion of the text
    :param end_column: The column number of the end of the desired portion of the text
    """
    # Convert 1-based indices provided by user to 0-based indices for Python string handling
    start_line -= 1
    start_column -= 1
    end_line -= 1
    end_column -= 1

    # Split the original text into lines
    lines = text.splitlines(keepends=True)

    # Get the text before the specified portion
    before_text = "".join(lines[:start_line]) + lines[start_line][:start_column]

    # Get the text after the specified portion
    after_text = lines[end_line][end_column:] + "".join(lines[end_line + 1 :])

    return before_text, after_text


def slice_text(
    text: str, start_line: int, start_column: int, end_line: int, end_column: int
) -> str:
    """
    Slice the text around the specified portion of the text.
    :param text: The text to slice
    :param start_line: The line number of the start of the desired portion of the text
    :param start_column: The column number of the start of the desired portion of the text
    :param end_line: The line number of the end of the desired portion of the text
    :param end_column: The column number of the end of the desired portion of the text
    """
    # Convert 1-based line and column numbers to 0-based indices
    start_line -= 1
    start_column -= 1
    end_line -= 1
    end_column -= 1

    # Split the text into lines
    lines = text.splitlines()

    # Extract the desired lines based on start and end line numbers
    sliced_lines = lines[start_line : end_line + 1]

    # Slice the desired lines based on start and end column numbers
    sliced_text = ""

    for i, line in enumerate(sliced_lines):
        if i == 0:
            # For the first line, slice from the start column to the end of the line
            sliced_text += line[start_column:] + "\n"
        elif i == len(sliced_lines) - 1:
            # For the last line, slice from the beginning of the line to the end column
            sliced_text += line[: end_column + 1]
        else:
            # For lines in between, add the whole line
            sliced_text += line + "\n"

    return sliced_text

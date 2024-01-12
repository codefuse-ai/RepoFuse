def slice_text_around(
    text: str, start_line: int, start_column: int, end_line: int, end_column: int
) -> tuple[str, str]:
    """
    Slice the text around the specified portion of the text.
    :param text: The text to slice
    :param start_line: The line number of the start of the desired portion of the text (1-based index)
    :param start_column: The column number of the start of the desired portion of the text (1-based index)
    :param end_line: The line number of the end of the desired portion of the text (1-based index)
    :param end_column: The column number of the end of the desired portion of the text (1-based index)
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
    Slice the text inside the specified portion of the text.
    :param text: The text to slice
    :param start_line: The line number of the start of the desired portion of the text (1-based index)
    :param start_column: The column number of the start of the desired portion of the text (1-based index)
    :param end_line: The line number of the end of the desired portion of the text (1-based index)
    :param end_column: The column number of the end of the desired portion of the text (1-based index)
    """
    lines = text.splitlines()
    start_index = (
        sum(len(lines[i]) + 1 for i in range(start_line - 1)) + start_column - 1
    )
    end_index = sum(len(lines[i]) + 1 for i in range(end_line - 1)) + end_column - 1
    return text[start_index:end_index]

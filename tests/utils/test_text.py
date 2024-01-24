import pytest

from dependency_graph.utils.text import slice_text_around, slice_text


# Test cases for slice_text_around
@pytest.mark.parametrize(
    "text, start_line, start_column, end_line, end_column, expected_before, expected_slice, expected_after",
    [
        ("Hello\nWorld", 2, 1, 2, 3, "Hello\n", "Wo", "rld"),
        ("Line 1\nLine 2\nLine 3", 2, 2, 3, 2, "Line 1\nL", "ine 2\nL", "ine 3"),
        ("One line only", 1, 5, 1, 8, "One ", "lin", "e only"),
        ("Multi\nline\ntext", 1, 1, 3, 4, "", "Multi\nline\ntex", "t"),
        ("Multi\nline\ntext", 2, 2, 2, 999, "Multi\nl", "ine\ntext", ""),
        # Add more test cases as needed
    ],
)
def test_slice_text_around(
    text,
    start_line,
    start_column,
    end_line,
    end_column,
    expected_before,
    expected_slice,
    expected_after,
):
    before, slice, after = slice_text_around(
        text, start_line, start_column, end_line, end_column
    )
    assert before == expected_before
    assert slice == expected_slice
    assert after == expected_after


# Test cases for slice_text
@pytest.mark.parametrize(
    "text, start_line, start_column, end_line, end_column, expected",
    [
        ("Hello\nWorld", 2, 1, 2, 3, "Wo"),
        ("Line 1\nLine 2\nLine 3", 2, 2, 3, 2, "ine 2\nL"),
        ("One line only", 1, 5, 1, 8, "lin"),
        ("Multi\nline\ntext", 1, 1, 3, 4, "Multi\nline\ntex"),
        # Add more test cases as needed
    ],
)
def test_slice_text(text, start_line, start_column, end_line, end_column, expected):
    sliced_text = slice_text(text, start_line, start_column, end_line, end_column)
    assert sliced_text == expected

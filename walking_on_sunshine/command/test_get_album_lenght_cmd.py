import pytest

from walking_on_sunshine.command.get_album_length_cmd import _format_album_name


@pytest.mark.parametrize(
    "test_input,expected",
    [("hello world", "album:hello%20world"), ("Rumours", "album:Rumours")],
)
def test_format_album_name(test_input, expected):
    output = _format_album_name(test_input)

    assert output == expected

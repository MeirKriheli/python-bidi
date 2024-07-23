from typing import AnyStr, Optional

from .bidi import get_display_inner


def get_display(
    str_or_bytes: AnyStr,
    encoding: str = "utf-8",
    base_dir: Optional[str] = None,
    debug: Optional[bool] = False,
) -> AnyStr:
    """Accepts string or bytes. In case of bytes, `encoding`
    is needed as the inner function expects a valid string (default:"utf-8").

    Set `upper_is_rtl` to True to treat upper case chars as strong 'R'
    for debugging (default: False).

    Set `base_dir` to 'L' or 'R' to override the calculated base_level.

    Set `debug` to True to return the calculated levels.

    Returns the display layout, either as unicode or `encoding` encoded
    string.

    """

    if isinstance(str_or_bytes, bytes):
        text = str_or_bytes.decode(encoding)
        was_decoded = True
    else:
        text = str_or_bytes
        was_decoded = False

    display = get_display_inner(text, base_dir, debug)

    if was_decoded:
        display = display.encode(encoding)

    return display

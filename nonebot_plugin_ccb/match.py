"""指令比對（不依賴 NoneBot，可單獨測試）。"""

from __future__ import annotations

from collections.abc import Iterable


def match_command(
    text: str, names: Iterable[str], *, require_slash: bool = False
) -> str | None:
    """text 以某個指令名開頭（可選 / 前綴）就回傳後面的參數，否則回傳 None。

    指令名後面必須是結尾或空白，所以 "ccb查询" 不會被當成 "ccb"，
    "ccbxyz"、"踩踩背真舒服" 這種普通聊天也不會觸發。
    """
    text = text.strip()
    if text.startswith("/"):
        text = text[1:].lstrip()
    elif require_slash:
        return None
    for name in sorted(names, key=len, reverse=True):
        if not text.lower().startswith(name.lower()):
            continue
        rest = text[len(name) :]
        if rest == "" or rest[0].isspace():
            return rest.strip()
    return None

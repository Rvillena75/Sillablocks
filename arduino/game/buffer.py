from __future__ import annotations


class BlockBuffer:
    """Keeps the physical cube sequence separate from the displayed text."""

    def __init__(self) -> None:
        self.blocks: list[str] = []

    def append(self, value: str) -> None:
        self.blocks.append(value)

    def delete_last(self) -> str | None:
        if not self.blocks:
            return None
        return self.blocks.pop()

    def clear(self) -> None:
        self.blocks.clear()

    def text(self) -> str:
        return "".join(self.blocks)

    def copy(self) -> list[str]:
        return list(self.blocks)

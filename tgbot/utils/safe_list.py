from __future__ import annotations

from contextlib import suppress


class SafeList(list):
    """
    Безопасный список.
    Не вызывает IndexError, а просто возвращает None
    """

    def __getitem__(self, index: int) -> ... | None:
        with suppress(IndexError):
            if isinstance(index, slice):
                return SafeList(super(SafeList, self).__getitem__(index))
            return super(SafeList, self).__getitem__(index)

    def __delitem__(self, index: int):
        with suppress(IndexError):
            return super(SafeList, self).__delitem__(index)

    def cleared(self) -> SafeList:
        """
        :return: Очищенный список.
        """
        self.clear()
        return self

import abc
import pathlib
from random import shuffle
from typing import NoReturn


class Pool(abc.ABC):
    pool: list = []

    def get_pool(self) -> list:
        return self.pool

    def __len__(self) -> int:
        return len(self.pool)

    @abc.abstractmethod
    def pop(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def info(self) -> dict:
        raise NotImplementedError

    @abc.abstractmethod
    def __init__(self):
        raise NotImplementedError

    @abc.abstractmethod
    def clear(self) -> NoReturn:
        raise NotImplementedError

    @abc.abstractmethod
    def reload(self) -> NoReturn:
        raise NotImplementedError


class FilePool(Pool):
    path = pathlib.Path()

    def pop(self) -> str:
        if len(self.pool) == 0:
            self.reload()
        value = self.pool.pop()
        return value

    def __init__(self):
        if not self.path.exists():
            self.path.write_text('')
        self.reload()

    def get_pool(self) -> list:
        self.reload()
        return self.pool

    def reload(self) -> NoReturn:
        with open(self.path, encoding='latin-1') as file:
            self.pool = file.read().split('\n')
            shuffle(self.pool)
            if '' in self.pool:
                self.pool.remove('')

    def clear(self) -> None:
        self.pool.clear()


class Factories:

    def __init__(self):
        ...

    def get(self, pool: str):
        ...

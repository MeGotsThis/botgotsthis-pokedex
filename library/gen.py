from typing import AsyncIterator

from lib.database import DatabaseMain


class Generation:
    def __init__(self,
                 database: DatabaseMain,
                 query: str,
                 game: str) -> None:
        self.database: DatabaseMain = database
        self.query: str = query
        self.game = game

    async def pokemonDex(self) -> AsyncIterator[str]:
        return
        yield

    async def pokemonEntry(self) -> AsyncIterator[str]:
        return
        yield

    async def pokemonIndex(self) -> AsyncIterator[str]:
        return
        yield

    async def pokemonMove(self) -> AsyncIterator[str]:
        return
        yield

    async def pokemonStats(self) -> AsyncIterator[str]:
        return
        yield

    async def pokemonLearn(self,
                           isFullLearn: bool,
                           isFullTmHm: bool,
                           isFullEgg: bool,
                           isFullTutoring: bool) -> AsyncIterator[str]:
        return
        yield

    async def pokemonEvolve(self) -> AsyncIterator[str]:
        return
        yield

    async def pokemonTmHm(self, isFull: bool) -> AsyncIterator[str]:
        return
        yield

    async def pokemonTm(self, isFull: bool) -> AsyncIterator[str]:
        return
        yield

    async def pokemonHm(self, isFull: bool) -> AsyncIterator[str]:
        return
        yield

    async def pokemonLocation(self, isFull: bool) -> AsyncIterator[str]:
        return
        yield

    async def pokemonWild(self, isFull: bool) -> AsyncIterator[str]:
        return
        yield

    async def pokemonSurf(self, isFull: bool) -> AsyncIterator[str]:
        return
        yield

    async def pokemonFish(self, isFull: bool) -> AsyncIterator[str]:
        return
        yield

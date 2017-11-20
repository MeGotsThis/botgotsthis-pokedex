from typing import AsyncIterator, Dict, Tuple, Type  # noqa: F401

from bot import data  # noqa: F401
from lib.cache import CacheStore
from lib.data import ChatCommandArgs
from lib.helper.chat import feature, permission

from .library import gen, gen1

pokemonGameVersions: Dict[str, Type[gen.Generation]] = {
    'red': gen1.Generation1,
    'blue': gen1.Generation1,
    'yellow': gen1.Generation1,
    }


async def _getGame(dataCache: CacheStore,
                   channel: 'data.Channel',
                   query: str) -> Tuple[str, gen.Generation]:
    game: str = await dataCache.getChatProperty(channel.channel, 'pokedexGame',
                                                'red')
    return game, pokemonGameVersions[game](query, game)


@feature('pokedex')
@permission('broadcaster')
async def commandPokeGame(args: ChatCommandArgs) -> bool:
    if len(args.message) < 2:
        game: str
        info: gen.Generation
        game, info = await _getGame(args.data, args.chat, args.message.query)
        args.chat.send(
            f'Bot Pokedex is currently set to {game[0].upper()}{game[1:]}')
        return True

    game = args.message.lower[1]
    if game not in pokemonGameVersions:
        args.chat.send('Unable to recognize the game')
        return True

    await args.data.setChatProperty(args.chat.channel, 'pokedexGame', game)
    args.chat.send(
        f'Set the Bot Pokedex to Pokemon {game[0].upper()}{game[1:]}')
    return True


@feature('pokedex')
@permission('moderator')
async def commandPokeDex(args: ChatCommandArgs) -> bool:
    if len(args.message) < 2:
        args.chat.send('Please specify a pokemon or a number')
        return True

    game: str
    info: gen.Generation
    game, info = await _getGame(args.data, args.chat, args.message.query)
    async with info:
        messages: AsyncIterator[str] = info.pokemonDex()
    args.chat.send([message async for message in messages])
    return True


@feature('pokedex')
@permission('moderator')
async def commandPokeEntry(args: ChatCommandArgs) -> bool:
    if len(args.message) < 2:
        args.chat.send('Please specify a pokemon or a number')
        return True

    game: str
    info: gen.Generation
    game, info = await _getGame(args.data, args.chat, args.message.query)
    async with info:
        messages: AsyncIterator[str] = info.pokemonEntry()
    args.chat.send([message async for message in messages])
    return True


@feature('pokedex')
@permission('moderator')
async def commandPokeIndex(args: ChatCommandArgs) -> bool:
    if len(args.message) < 2:
        args.chat.send('Please specify a number')
        return True

    game: str
    info: gen.Generation
    game, info = await _getGame(args.data, args.chat, args.message.query)
    async with info:
        messages: AsyncIterator[str] = info.pokemonIndex()
    args.chat.send([message async for message in messages])
    return True


@feature('pokedex')
@permission('moderator')
async def commandPokeMove(args: ChatCommandArgs) -> bool:
    if len(args.message) < 2:
        args.chat.send('Please specify a pokemon or a number')
        return True

    game: str
    info: gen.Generation
    game, info = await _getGame(args.data, args.chat, args.message.query)
    async with info:
        messages: AsyncIterator[str] = info.pokemonMove()
    args.chat.send([message async for message in messages])
    return True


@feature('pokedex')
@permission('moderator')
async def commandPokeStats(args: ChatCommandArgs) -> bool:
    if len(args.message) < 2:
        args.chat.send('Please specify a pokemon or a number')
        return True

    game: str
    info: gen.Generation
    game, info = await _getGame(args.data, args.chat, args.message.query)
    async with info:
        messages: AsyncIterator[str] = info.pokemonStats()
    args.chat.send([message async for message in messages])
    return True


@feature('pokedex')
@permission('moderator')
async def commandPokeEvolve(args: ChatCommandArgs) -> bool:
    if len(args.message) < 2:
        args.chat.send('Please specify a pokemon or a number')
        return True

    game: str
    info: gen.Generation
    game, info = await _getGame(args.data, args.chat, args.message.query)
    async with info:
        messages: AsyncIterator[str] = info.pokemonEvolve()
    args.chat.send([message async for message in messages])
    return True


@feature('pokedex')
@permission('moderator')
async def commandPokeLearn(args: ChatCommandArgs) -> bool:
    if len(args.message) < 2:
        args.chat.send('Please specify a pokemon or a number or a move')
        return True

    game: str
    info: gen.Generation
    game, info = await _getGame(args.data, args.chat, args.message.query)
    messages: AsyncIterator[str]
    async with info:
        messages = info.pokemonLearn(
            args.message.command.endswith(('-full', '-level')),
            args.message.command.endswith(('-full', '-tmhm')),
            args.message.command.endswith(('-full', '-egg')),
            args.message.command.endswith(('-full', '-tutor')))
    args.chat.send([message async for message in messages])
    return True


@feature('pokedex')
@permission('moderator')
async def commandPokeTmHms(args: ChatCommandArgs) -> bool:
    if len(args.message) < 2:
        args.chat.send('Please specify a move')
        return True

    game: str
    info: gen.Generation
    game, info = await _getGame(args.data, args.chat, args.message.query)
    messages: AsyncIterator[str]
    async with info:
        messages = info.pokemonTmHm(args.message.command.endswith('-full'))
    args.chat.send([message async for message in messages])
    return True


@feature('pokedex')
@permission('moderator')
async def commandPokeTm(args: ChatCommandArgs) -> bool:
    if len(args.message) < 2:
        args.chat.send('Please specify a number')
        return True

    game: str
    info: gen.Generation
    game, info = await _getGame(args.data, args.chat, args.message.query)
    messages: AsyncIterator[str]
    async with info:
        messages = info.pokemonTm(args.message.command.endswith('-full'))
    args.chat.send([message async for message in messages])
    return True


@feature('pokedex')
@permission('moderator')
async def commandPokeHm(args: ChatCommandArgs) -> bool:
    if len(args.message) < 2:
        args.chat.send('Please specify a number')
        return True

    game: str
    info: gen.Generation
    game, info = await _getGame(args.data, args.chat, args.message.query)
    messages: AsyncIterator[str]
    async with info:
        messages = info.pokemonHm(args.message.command.endswith('-full'))
    args.chat.send([message async for message in messages])
    return True


@feature('pokedex')
@permission('moderator')
async def commandPokeLocation(args: ChatCommandArgs) -> bool:
    if len(args.message) < 2:
        args.chat.send('Please specify a location or a number')
        return True

    game: str
    info: gen.Generation
    game, info = await _getGame(args.data, args.chat, args.message.query)
    messages: AsyncIterator[str]
    async with info:
        messages = info.pokemonLocation(args.message.command.endswith('-full'))
    args.chat.send([message async for message in messages])
    return True


@feature('pokedex')
@permission('moderator')
async def commandPokeWild(args: ChatCommandArgs) -> bool:
    if len(args.message) < 2:
        args.chat.send('Please specify a location or a number')
        return True

    game: str
    info: gen.Generation
    game, info = await _getGame(args.data, args.chat, args.message.query)
    messages: AsyncIterator[str]
    async with info:
        messages = info.pokemonWild(args.message.command.endswith('-full'))
    args.chat.send([message async for message in messages])
    return True


@feature('pokedex')
@permission('moderator')
async def commandPokeSurf(args: ChatCommandArgs) -> bool:
    if len(args.message) < 2:
        args.chat.send('Please specify a location or a number')
        return True

    game: str
    info: gen.Generation
    game, info = await _getGame(args.data, args.chat, args.message.query)
    messages: AsyncIterator[str]
    async with info:
        messages = info.pokemonSurf(args.message.command.endswith('-full'))
    args.chat.send([message async for message in messages])
    return True


@feature('pokedex')
@permission('moderator')
async def commandPokeFish(args: ChatCommandArgs) -> bool:
    if len(args.message) < 2:
        args.chat.send('Please specify a location or a number')
        return True

    game: str
    info: gen.Generation
    game, info = await _getGame(args.data, args.chat, args.message.query)
    messages: AsyncIterator[str]
    async with info:
        messages = info.pokemonFish(args.message.command.endswith('-full'))
    args.chat.send([message async for message in messages])
    return True

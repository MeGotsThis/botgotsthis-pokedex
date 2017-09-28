from typing import Iterable, Mapping, Optional

from lib.data import ChatCommand

from .. import channel


def filterMessage() -> Iterable[ChatCommand]:
    return []


def commands() -> Mapping[str, Optional[ChatCommand]]:
    if not hasattr(commands, 'commands'):
        setattr(commands, 'commands', {
            '!pokegame': channel.commandPokeGame,
            '!pokedex': channel.commandPokeDex,
            '!pokeentry': channel.commandPokeEntry,
            '!pokeindex': channel.commandPokeIndex,
            '!pokemove': channel.commandPokeMove,
            '!pokestats': channel.commandPokeStats,
            '!pokeevolve': channel.commandPokeEvolve,
            '!pokelearn': channel.commandPokeLearn,
            '!pokelearn-level': channel.commandPokeLearn,
            '!pokelearn-tmhm': channel.commandPokeLearn,
            '!pokelearn-egg': channel.commandPokeLearn,
            '!pokelearn-tutor': channel.commandPokeLearn,
            '!pokelearn-full': channel.commandPokeLearn,
            '!poketmhm': channel.commandPokeTmHms,
            '!poketmhm-full': channel.commandPokeTmHms,
            '!poketm': channel.commandPokeTm,
            '!poketm-full': channel.commandPokeTm,
            '!pokehm': channel.commandPokeHm,
            '!pokehm-full': channel.commandPokeHm,
            '!pokelocation': channel.commandPokeLocation,
            '!pokelocation-full': channel.commandPokeLocation,
            '!pokewild': channel.commandPokeWild,
            '!pokewild-full': channel.commandPokeWild,
            '!pokesurf': channel.commandPokeSurf,
            '!pokesurf-full': channel.commandPokeSurf,
            '!pokefish': channel.commandPokeFish,
            '!pokefish-full': channel.commandPokeFish,
            }
        )
    return getattr(commands, 'commands')


def commandsStartWith() -> Mapping[str, Optional[ChatCommand]]:
    return {}


def processNoCommand() -> Iterable[ChatCommand]:
    return []

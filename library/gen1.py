import bot

import aioodbc.cursor  # noqa: F401

from contextlib import suppress
from typing import AsyncIterator, Dict, List, Optional, Tuple  # noqa: F401

from .gen import Generation

_encounterRate256: Tuple[int, ...]
_encounterRate256 = 51, 51, 39, 25, 25, 25, 13, 13, 11, 3


class Generation1(Generation):
    async def _attachDatabase(self) -> None:
        if not self.database.isSqlite:
            return
        cursor: aioodbc.cursor.Cursor
        query: str
        async with await self.database.cursor() as cursor:
            query = 'ATTACH DATABASE ? AS gen1'
            await cursor.execute(query, ('sqlite/gen1.sqlite',))

    async def _getGameVersionIds(self) -> Tuple[int, int]:
        cursor: aioodbc.cursor.Cursor
        query: str
        async with await self.database.cursor() as cursor:
            query = '''
SELECT gen1_game_versions.id, gen1_games.id
    FROM gen1_game_versions, gen1_games
    WHERE gen1_game_versions.shortName=?
        AND gen1_games.id=gen1_game_versions.gameIndex'''
            await cursor.execute(query, (self.game,))
            row: Tuple[int, int] = await cursor.fetchone() or (0, 0)
            return row[1], row[0],

    async def _queryPokemon(self) -> Optional[int]:
        cursor: aioodbc.cursor.Cursor
        query: str
        async with await self.database.cursor() as cursor:
            pokemonId: Optional[int] = None
            q: int
            if pokemonId is None:
                with suppress(ValueError):
                    q = int(self.query)
                    if 1 <= q <= 151:
                        pokemonId = q
            if pokemonId is None:
                try:
                    if self.query[0:2].lower() != '0x':
                        raise Exception()
                    q = int(self.query[2:], 16)
                    query = '''
SELECT pokedexNumber FROM gen1_pokemon WHERE gameIndexNumber=?
'''
                    await cursor.execute(query, (q,))
                    pokemonId, = await cursor.fetchone()
                except Exception:
                    pass
            if pokemonId is None:
                try:
                    query = '''
SELECT pokedexNumber FROM gen1_pokemon WHERE LOWER(name)=?
'''
                    await cursor.execute(query, (self.query.lower(),))
                    pokemonId, = await cursor.fetchone()
                except Exception:
                    pass
            return pokemonId

    async def _queryMove(self,
                         isTM: bool=False,
                         isHM: bool=False) -> Optional[int]:
        cursor: aioodbc.cursor.Cursor
        query: str
        async with await self.database.cursor() as cursor:
            moveId: Optional[int] = None
            q: int
            if isHM and moveId is None:
                try:
                    q = int(self.query)
                    query = '''
SELECT gameIndexNumber FROM gen1_moves WHERE hmNumber=?
'''
                    await cursor.execute(query, (q,))
                    moveId, = await cursor.fetchone()
                except Exception:
                    pass
            if isTM and moveId is None:
                try:
                    q = int(self.query)
                    query = '''
SELECT gameIndexNumber FROM gen1_moves WHERE tmNumber=?
'''
                    await cursor.execute(query, (q,))
                    moveId, = await cursor.fetchone()
                except Exception:
                    pass
            if not isHM and not isTM and moveId is None:
                try:
                    q = int(self.query)
                    if 1 <= q <= 165:
                        moveId = q
                except Exception:
                    pass
            if not isHM and not isTM and moveId is None:
                try:
                    if self.query[0:2].lower() != '0x':
                        raise Exception()
                    q = int(self.query[2:], 16)
                    if 1 <= q <= 165:
                        moveId = q
                except Exception:
                    pass
            if moveId is None:
                try:
                    query = '''
SELECT gameIndexNumber FROM gen1_moves WHERE LOWER(name)=?
'''
                    await cursor.execute(query, (query.lower(),))
                    moveId, = await cursor.fetchone()
                except Exception:
                    pass
            return moveId

    async def _queryLocation(self, version: Tuple[int, int]) -> Optional[int]:
        cursor: aioodbc.cursor.Cursor
        query: str
        async with await self.database.cursor() as cursor:
            locationId: Optional[int] = None
            q: int
            if locationId is None:
                try:
                    query = '''
SELECT mapIndex
    FROM gen1_locations
    WHERE mapIndex=?
        AND EXISTS(
            SELECT 1
                FROM gen1_location_used
                WHERE gen1_location_used.mapIndex=gen1_locations.mapIndex
                    AND gen1_location_used.versionId=?)
'''
                    q = int(self.query)
                    await cursor.execute(query, (q, version[1]))
                    locationId, = await cursor.fetchone()
                except Exception:
                    pass
            if locationId is None:
                try:
                    if self.query[0:2].lower() != '0x':
                        raise Exception()
                    q = int(self.query[2:], 16)
                    query = '''
SELECT mapIndex
    FROM gen1_locations
    WHERE mapIndex=?
    AND EXISTS(
        SELECT 1
            FROM gen1_location_used
            WHERE gen1_location_used.mapIndex=gen1_locations.mapIndex
                AND gen1_location_used.versionId=?)
'''
                    await cursor.execute(query, (q, version[1]))
                    locationId, = await cursor.fetchone()
                except Exception:
                    pass
            if locationId is None:
                try:
                    query = '''
SELECT mapIndex
    FROM gen1_locations
    WHERE LOWER(name)=?
    AND EXISTS(
        SELECT 1
            FROM gen1_location_used
            WHERE gen1_location_used.mapIndex=gen1_locations.mapIndex
                AND gen1_location_used.versionId=?)
'''
                    await cursor.execute(query, (query.lower(), version[1]))
                    locationId, = await cursor.fetchone()
                except Exception:
                    pass
            return locationId

    async def pokemonDex(self) -> AsyncIterator[str]:
        await self._attachDatabase()
        gameIds: Tuple[int, int] = await self._getGameVersionIds()
        pokemonId: Optional[int] = await self._queryPokemon()
        if pokemonId is None:
            yield 'Pokemon Not Found'
            return
        cursor: aioodbc.cursor.Cursor
        query: str
        async with await self.database.cursor() as cursor:
            query = '''
SELECT pokedexNumber, name, heightMeters, weightKilograms,
        (SELECT entry
            FROM gen1_pokedex_entries AS pokedex
            WHERE pokedex.pokedexNumber=gen1_pokemon.pokedexNumber
                AND pokedex.versionId=?)
    FROM gen1_pokemon
    WHERE pokedexNumber=?
'''
            await cursor.execute(query, (gameIds[1], int(pokemonId),))
            pokemon: Tuple[int, str, float, float, str]
            pokemon = await cursor.fetchone()
            weightLbs: float = round(float(pokemon[3]) * 2.205)
            if weightLbs == 0:
                weightLbs = round(float(pokemon[3]) * 2.205, 1)
            heightInches: int = round(float(pokemon[2]) * 39.3701)
            pokedex: str = pokemon[4].replace('\n', ' ').replace('\x0c', ' ')

            yield f'''\
Pokemon Name: {pokemon[1]}, Pokedex Number: {pokemon[0]}, \
Weight: {weightLbs:.1f}lbs ({pokemon[3]:.1f}kg), \
Height: {heightInches // 12}'{heightInches % 12}" ({pokemon[2]:.1f}m)'''
            yield f'Pokedex: {pokedex}'

    async def pokemonEntry(self) -> AsyncIterator[str]:
        await self._attachDatabase()
        gameIds: Tuple[int, int] = await self._getGameVersionIds()
        pokemonId: Optional[int] = await self._queryPokemon()
        if pokemonId is None:
            yield 'Pokemon Not Found'
            return
        cursor: aioodbc.cursor.Cursor
        query: str
        async with await self.database.cursor() as cursor:
            query = '''
SELECT pokedexNumber, gameIndexNumber, name,
        (SELECT typeName
            FROM gen1_types
            WHERE gen1_types.typeIndex=gen1_pokemon.type1) AS type1,
        (SELECT typeName
            FROM gen1_types
            WHERE gen1_types.typeIndex=gen1_pokemon.type2) AS type2,
        (SELECT name
            FROM gen1_experiencecurve
            WHERE gen1_experiencecurve.curveIndex=gen1_pokemon.experienceCurve
            ) AS experienceCurve,
        catchRate, heightMeters, weightKilograms, baseHP, baseAttack,
        baseDefense, baseSpeed, baseSpecial
    FROM gen1_pokemon
    WHERE pokedexNumber=?
'''
            await cursor.execute(query, (pokemonId,))
            pokemon: Optional[Tuple[int,  # 0: pokedexNumber
                                    int,  # 1: gameIndexNumber
                                    str,  # 2: name
                                    str,  # 3: type1
                                    Optional[str],  # 4: type2
                                    str,  # 5: experienceCurve
                                    int,  # 6: catchRate
                                    int,  # 7: heightMeters
                                    int,  # 8: weightKilograms
                                    int,  # 9: baseHP
                                    int,  # 10: baseAttack
                                    int,  # 11: baseDefense
                                    int,  # 12: baseSpeed
                                    int,  # 13: baseSpecial
                                    ]]
            pokemon = await cursor.fetchone()
            if pokemon is None:
                yield 'Pokemon Not Found'
                return
            pokemonType: str = pokemon[3]
            if pokemon[4]:
                pokemonType += '/' + pokemon[4]
            weightLbs: float = round(float(pokemon[8]) * 2.205)
            if weightLbs == 0:
                weightLbs = round(float(pokemon[8]) * 2.205, 1)
            heightInches: int = round(float(pokemon[7]) * 39.3701)

            yield f'''\
Pokemon Name: {pokemon[2]}, Pokedex Number: {pokemon[0]}, \
Pokemon Index: 0x{pokemon[1]:02X} ({pokemon[1]}), Type: {pokemonType}'''
            yield f'''\
Catch Rate: {pokemon[6]}, Experience Curve: {pokemon[5]}, \
Weight: {weightLbs:.1f}lbs ({pokemon[8]:.1f}kg), \
Height: {heightInches // 12}'{heightInches % 12}" ({pokemon[7]:.1f}m)'''
            yield f'''\
Base Stats HP: {pokemon[9]}, Attack: {pokemon[10]}, Defense: {pokemon[11]}, \
Speed: {pokemon[12]}, Special: {pokemon[13]}'''

            query = '''
SELECT levelUp, COUNT(*)
    FROM gen1_pokemon_levelup
    WHERE pokedexNumber=?
        AND gameIndex=?
    GROUP BY levelUp
    ORDER BY levelUp ASC
'''
            levels: List[str] = []
            params: Tuple[int, int] = (pokemonId, gameIds[0])
            level: int
            count: int
            async for level, count in await cursor.execute(query, params):
                if int(level) == 1:
                    if int(count) > 1:
                        levels.append(f'---({count})')
                    else:
                        levels.append('---')
                else:
                    levels.append(f'L{level}')
            message: str = 'Learn Moves at: ' + ', '.join(levels)
            query = '''
SELECT COUNT(*)
    FROM gen1_pokemon_tmhmcompatability AS tmhm
    WHERE pokedexNumber=?
        AND gameIndex=?
        AND (SELECT tmNumber
                FROM gen1_moves
                 WHERE gen1_moves.gameIndexNumber=tmhm.moveIndex
             ) IS NOT NULL
'''
            await cursor.execute(query, (pokemonId, gameIds[0],))
            tmCount: int
            tmCount, = await cursor.fetchone() or (0,)
            message += f'; Learns {tmCount} TMs'
            query = '''
SELECT (SELECT name
            FROM gen1_moves
            WHERE gen1_moves.gameIndexNumber=tmhm.moveIndex)
    FROM gen1_pokemon_tmhmcompatability AS tmhm
    WHERE pokedexNumber=?
        AND gameIndex=?
        AND (SELECT hmNumber
                FROM gen1_moves
                WHERE gen1_moves.gameIndexNumber=tmhm.moveIndex
            ) IS NOT NULL
'''
            hms: List[str] = []
            move: str
            async for move, in await cursor.execute(query, params):
                hms.append(move)
            if hms:
                message += '; ' + ', '.join(hms)
            yield message

    async def pokemonIndex(self) -> AsyncIterator[str]:
        await self._attachDatabase()
        gameIds: Tuple[int, int] = await self._getGameVersionIds()
        cursor: aioodbc.cursor.Cursor
        query: str
        async with await self.database.cursor() as cursor:
            number: Optional[int] = None
            if number is None:
                try:
                    number = int(self.query)
                except Exception:
                    pass
            if number is None:
                try:
                    if self.query[0:2].lower() != '0x':
                        raise Exception()
                    number = int(self.query[2:], 16)
                except Exception:
                    pass
            if number is None:
                yield 'Invalid number entered'
                return
            messages: List[str] = []
            name: str

            query = 'SELECT name FROM gen1_pokemon WHERE pokedexNumber=?'
            await cursor.execute(query, (number,))
            name, = await cursor.fetchone() or (None,)
            if name:
                messages.append(f'Pokemon by Dex number: {name}')

            query = 'SELECT name FROM gen1_pokemon WHERE gameIndexNumber=?'
            await cursor.execute(query, (number,))
            name, = await cursor.fetchone() or (None,)
            if name:
                if messages:
                    messages.append(f'by Index number: {name}')
                else:
                    messages.append(f'Pokemon by Index number: {name}')

            queries: List[Tuple[str, str]] = [
                ('SELECT name FROM gen1_moves WHERE gameIndexNumber=?',
                 'Move'),
                ('SELECT name FROM gen1_items WHERE hexIndex=?', 'Item'),
                ('SELECT name FROM gen1_experiencecurve WHERE curveIndex=?',
                 'Experience Curve'),
                ('SELECT typeName FROM gen1_types WHERE typeIndex=?', 'Type'),
                ('SELECT className FROM gen1_trainer_class WHERE gameIndex=?',
                 'Trainer Class'),
                ]
            for query, item in queries:
                await cursor.execute(query, (number,))
                name, = await cursor.fetchone() or (None,)
                if name:
                    messages.append(f'{item}: {name}')
            queries = [
                ('''
SELECT name
    FROM gen1_locations
    WHERE mapIndex=?
        AND EXISTS(
            SELECT 1
                FROM gen1_location_used
                WHERE gen1_locations.mapIndex=gen1_location_used.mapIndex
                    AND gen1_location_used.versionId=?)
''',
                 'Location'),
            ]
            for query, item in queries:
                await cursor.execute(query, (int(number), gameIds[1],))
                name, = await cursor.fetchone() or (None,)
                if name:
                    messages.append(f'{item}: {name}')
            if not messages:
                yield 'Nothing found'
                return
            yield ', '.join(messages)

    async def pokemonMove(self) -> AsyncIterator[str]:
        def stageFormat(prefix: str, by: int, stat: str, who: str) -> str:
            if by <= -2:
                return f'{prefix} double decrease the {stat} stat on {who}'
            if by == -1:
                return f'{prefix} decrease the {stat} stat on {who}'
            if by == 1:
                return f'{prefix} increase the {stat} stat on {who}'
            if by >= 2:
                return f'{prefix} double increase the {stat} stat on {who}'
            return ''

        await self._attachDatabase()
        gameIds: Tuple[int, int] = await self._getGameVersionIds()
        moveId: Optional[int] = await self._queryMove()
        if moveId is None:
            yield 'Move Not Found'
            return
        cursor: aioodbc.cursor.Cursor
        query: str
        async with await self.database.cursor() as cursor:
            query = '''
SELECT gameIndexNumber, name,
        (SELECT typeName
            FROM gen1_types
            WHERE gen1_types.typeIndex=gen1_moves.typeIndex) AS type,
        basePower, basePP, accuracy, tmNumber, hmNumber, targetEnemy,
        hasChargingTurn, healRate, drainRate, primaryEffect, secondEffect,
        secondEffectChance, staticDamage, effectMinTurns, effectMaxTurns,
        enemyStageModifier, attackStageModifier, defenseStageModifier,
        speedStageModifier, specialStageModifier, accuracyStageModifier,
        evasionStageModifier
    FROM gen1_moves
    WHERE gameIndexNumber=?'''
            await cursor.execute(query, (moveId,))
            move: Optional[Tuple[int,  # 0: gameIndexNumber
                                 str,  # 1: name
                                 str,  # 2: type
                                 Optional[int],  # 3: basePower
                                 Optional[int],  # 4: basePP
                                 Optional[int],  # 5: accuracy
                                 Optional[int],  # 6: tmNumber
                                 Optional[int],  # 7: hmNumber
                                 bool,  # 8: targetEnemy
                                 bool,  # 9: hasChargingTurn
                                 Optional[float],  # 10: healRate
                                 Optional[float],  # 11: drainRate
                                 Optional[str],  # 12: primaryEffect
                                 Optional[str],  # 13: secondEffect
                                 Optional[float],  # 14: secondEffectChance
                                 Optional[float],  # 15: staticDamage
                                 Optional[float],  # 16: effectMinTurns
                                 Optional[float],  # 17: effectMaxTurns
                                 Optional[bool],  # 18: enemyStageModifier
                                 Optional[int],  # 19: attackStageModifier
                                 Optional[int],  # 20: defenseStageModifier
                                 Optional[int],  # 21: speedStageModifier
                                 Optional[int],  # 22: specialStageModifier
                                 Optional[int],  # 23: accuracyStageModifier
                                 Optional[int],  # 24: evasionStageModifier
                                 ]]
            move = await cursor.fetchone()
            yield f'''\
Move Name: {move[1]}, Move Index: {move[0]}, Type: {move[2]}, \
Base Power: {move[3]}, PP: {move[4]}, Accuracy: {move[5]}'''
            properties = []
            if move[8]:
                properties.append('Targets enemy')
            else:
                properties.append('Targets self')
            if move[9]:
                properties.append('Has Charging Turn')
            if move[10] and not move[12]:
                properties.append(f'Heals {move[10]}% of Max HP')
            if move[12] == 'badlyPoison':
                properties.append('Badly Poisons the enemy')
            elif move[12] == 'bide':
                properties.append(
                    'Wait 2 turns, Returns twice damage received')
            elif move[12] == 'boom':
                properties.append('Faints, Enemy defense will be halved')
            elif move[12] == 'confusion':
                properties.append('Applies Confusion status')
            elif move[12] == 'conversion':
                properties.append('Changes user type to enemy type')
            elif move[12] == 'counter':
                properties.append('''\
Returns twitce damage received from a Normal or Fighting move''')
            elif move[12] == 'crash':
                properties.append('User receive 1 HP damage if missed')
            elif move[12] == 'disable':
                properties.append(f'''\
Disables one of enemy moves for {move[16]} - {move[17]} turns''')
            elif move[12] == 'fatigue':
                properties.append(f'''\
Consecutively attacks for {move[16]} - {move[17]} turns, afterwards user is \
confused''')
            elif move[12] == 'flee' or move[12] == 'phazing':
                properties.append('Escape an wild encounter')
            elif move[12] == 'fly':
                properties.append(
                    'On Charging turn, user is semi-invulnerable')
            elif move[12] == 'focusEnergy':
                properties.append('Decreases chance of critical hit by 4')
            elif move[12] == 'haze':
                properties.append('Reset some of in-battle effects')
            elif move[12] == 'highCrit':
                properties.append('High Critical-hit ratio')
            elif move[12] == 'leechSeed':
                p = 'Plant a seed at the target, drains 1/16 HP per turn'
                properties.append(p)
            elif move[12] == 'levelDamage':
                properties.append('Applies damage equal to user level')
            elif move[12] == 'lightscreen':
                properties.append('Doubles the users effective Special')
            elif move[12] == 'metronome':
                properties.append('Executes a random move')
            elif move[12] == 'mimic':
                properties.append('Copies a move the enemy has')
            elif move[12] == 'mirrorMove':
                properties.append('Uses the last move the enemy used on user')
            elif move[12] == 'mist':
                properties.append('Prevents stat modifications from enemy')
            elif move[12] == 'multihit':
                properties.append(f'''\
Execute the move {move[16]} - {move[17]} times in same turn''')
            elif move[12] == 'ohko':
                properties.append('One Hit KO if user is faster')
            elif move[12] == 'paralyze':
                properties.append('Paralyzes the enemy')
            elif move[12] == 'payday':
                properties.append("Scatter coins twice the user's level")
            elif move[12] == 'poison':
                properties.append("Poisons the enemy")
            elif move[12] == 'psywave':
                properties.append('''\
Deals Random amount of damage from 0.5 to 1.5 or the user's level''')
            elif move[12] == 'rage':
                properties.append('''\
Locks the user to only use Rage, user Attack will increase if hit by enemy''')
            elif move[12] == 'recharge':
                properties.append('User needs to recharge after executed')
            elif move[12] == 'reflect':
                properties.append('Doubles the users effective Defense')
            elif move[12] == 'reset':
                properties.append('''\
Heals to full, Remove all status ailment, Sleeps for 2 turns''')
            elif move[12] == 'sleep':
                properties.append('Sleep the enemy')
            elif move[12] == 'stage':
                prefix = 'Applies'
                who = 'enemy' if move[18] else 'self'
                stage = ''
                if move[19] is not None:
                    stage = stageFormat(prefix, move[19], 'Attack', who)
                if move[20] is not None:
                    stage = stageFormat(prefix, move[20], 'Defense', who)
                if move[21] is not None:
                    stage = stageFormat(prefix, move[21], 'Speed', who)
                if move[22] is not None:
                    stage = stageFormat(prefix, move[22], 'Special', who)
                if move[23] is not None:
                    stage = stageFormat(prefix, move[23], 'Accuracy', who)
                if move[24] is not None:
                    stage = stageFormat(prefix, move[24], 'Evasion', who)
                properties.append(stage)
            elif move[12] == 'static':
                properties.append(f'Deals {move[15]} damage')
            elif move[12] == 'substitute':
                properties.append(
                    'Create a substitute using 25% of user Max HP')
            elif move[12] == 'superFang':
                properties.append(
                    'Deals damage equal to half enemy current HP')
            elif move[12] == 'targetSleep':
                properties.append('Deals damage when the enemy is asleep')
            elif move[12] == 'transform':
                properties.append('Transforms as the enemy')
            elif move[12] == 'trap':
                properties.append('Traps the enemy')
            if move[13]:
                chance = f'{move[14] / 256 * 100:.1f}%'
                if move[13] == 'burn':
                    properties.append(f'{chance} to burn the enemy')
                elif move[13] == 'confusion':
                    properties.append(f'{chance} to confuse the enemy')
                elif move[13] == 'flinch':
                    properties.append(f'{chance} to flinch the enemy')
                elif move[13] == 'freeze':
                    properties.append(f'{chance}to freeze the enemy')
                elif move[13] == 'paralyze':
                    properties.append(f'{chance} to paralyze the enemy')
                elif move[13] == 'poison':
                    properties.append(f'{chance} to poison the enemy')
                elif move[13] == 'stage':
                    prefix = f'{chance} to'
                    who = 'enemy' if move[18] else 'self'
                    stage = ''
                    if move[19] is not None:
                        stage = stageFormat(prefix, move[19], 'Attack', who)
                    if move[20] is not None:
                        stage = stageFormat(prefix, move[20], 'Defense', who)
                    if move[21] is not None:
                        stage = stageFormat(prefix, move[21], 'Speed', who)
                    if move[22] is not None:
                        stage = stageFormat(prefix, move[22], 'Special', who)
                    if move[23] is not None:
                        stage = stageFormat(prefix, move[23], 'Accuracy', who)
                    if move[24] is not None:
                        stage = stageFormat(prefix, move[24], 'Evasion', who)
                    properties.append(stage)
            if move[11]:
                if move[11] > 0:
                    properties.append(f'Recovers {move[11]}% of Damage Done')
                if move[11] < 0:
                    properties.append(f'Recoils {-move[11]}% of Damage Done')
            yield ', '.join(properties)

            query = '''
SELECT COUNT(DISTINCT pokedexNumber), levelUp=1
    FROM gen1_pokemon_levelup
    WHERE moveIndex=? AND gameIndex=?
    GROUP BY levelUp=1
    ORDER BY levelUp=1
'''
            count: Dict[bool, int] = {False: 0, True: 0}
            moveCount: int
            starts: bool
            await cursor.execute(query, (moveId, gameIds[0]))
            async for moveCount, starts in cursor:
                count[bool(starts)] = moveCount
            if count[True] > 0:
                yield f'{count[True]} Pokemon starts with this move'
            if count[False] > 0:
                yield f'{count[False]} Pokemon learns this move'

            if move[6] is not None or move[7] is not None:
                query = '''
SELECT COUNT(DISTINCT pokedexNumber)
    FROM gen1_pokemon_tmhmcompatability
    WHERE moveIndex=? AND gameIndex=?
'''
                await cursor.execute(query, (moveId, gameIds[0]))
                tmhmCount: int
                tmhmCount, = await cursor.fetchone() or (0,)
                item: str
                if move[6] is not None:
                    item = f'TM{move[6]:02}'
                else:
                    item = f'HM{move[7]:02}'
                yield f'{tmhmCount} Pokemon learns {item}'

    async def pokemonStats(self) -> AsyncIterator[str]:
        await self._attachDatabase()
        pokemonId: Optional[int] = await self._queryPokemon()
        if pokemonId is None:
            yield 'Pokemon Not Found'
            return
        cursor: aioodbc.cursor.Cursor
        query: str
        async with await self.database.cursor() as cursor:
            query = '''
SELECT pokedexNumber, name, baseHP, baseAttack, baseDefense, baseSpeed,
        baseSpecial
    FROM gen1_pokemon
    WHERE pokedexNumber=?
'''
            await cursor.execute(query, (pokemonId,))
            pokemon: Optional[Tuple[int,  # 0: pokedexNumber
                                    str,  # 1: name
                                    int,  # 2: baseHP
                                    int,  # 3: baseAttack
                                    int,  # 4: baseDefense
                                    int,  # 5: baseSpeed
                                    int,  # 6: baseSpecial
                                    ]]
            pokemon = await cursor.fetchone()
            if pokemon is None:
                yield 'Pokemon Not Found'
                return
            yield f'Pokemon Name: {pokemon[1]}, Pokedex Number: {pokemon[0]}'
            yield f'''\
Base Stats HP: {pokemon[2]}, Attack: {pokemon[3]}, Defense: {pokemon[4]}, \
Speed: {pokemon[5]}, Special: {pokemon[6]}'''

    async def pokemonLearn(self,
                           isFullLearn: bool,
                           isFullTmHm: bool,
                           isFullEgg: bool,
                           isFullTutoring: bool) -> AsyncIterator[str]:
        await self._attachDatabase()
        gameIds: Tuple[int, int] = await self._getGameVersionIds()
        cursor: aioodbc.cursor.Cursor
        query: str
        async with await self.database.cursor() as cursor:
            params: Tuple[int, int]
            levelUp: int
            name: str
            count: int
            level: str

            pokemonId: Optional[int] = await self._queryPokemon()
            if pokemonId is not None:
                query = '''
SELECT pokedexNumber, name FROM gen1_pokemon WHERE pokedexNumber=?'''
                await cursor.execute(query, (pokemonId,))
                dex: int
                name, dex = await cursor.fetchone() or ('', 0)
                if name:
                    yield f'Pokemon Name: {name}, Pokedex Number: {dex}'

                params = pokemonId, gameIds[0],
                if isFullLearn:
                    query = '''
SELECT l.levelUp, m.name
    FROM gen1_pokemon_levelup AS l, gen1_moves AS m
    WHERE l.moveIndex=m.gameIndexNumber
        AND l.pokedexNumber=?
        AND l.gameIndex=?
    ORDER BY l.levelUp ASC, l.levelUpOrder ASC
'''
                    await cursor.execute(query, params)
                    async for levelUp, name in cursor:
                        if levelUp == 1:
                            level = '---'
                        else:
                            level = f'L{levelUp}'
                        yield f'{level}: {name}'
                else:
                    query = '''
SELECT levelUp, COUNT(*)
    FROM gen1_pokemon_levelup
    WHERE pokedexNumber=? AND gameIndex=?
    GROUP BY levelUp
    ORDER BY levelUp ASC
'''
                    levels: List[str] = []
                    await cursor.execute(query, params)
                    async for levelUp, count in cursor:
                        if levelUp == 1:
                            if count > 1:
                                levels.append(f'---({count})')
                            else:
                                levels.append('---')
                        else:
                            levels.append(f'L{levelUp}')
                    yield 'Learn Moves at: ' + ', '.join(levels)

                if isFullTmHm:
                    message: str
                    query = '''
SELECT m.name, m.tmNumber
    FROM gen1_pokemon_tmhmcompatability AS c, gen1_moves AS m
    WHERE c.pokedexNumber=?
        AND c.gameIndex=?
        AND m.gameIndexNumber=c.moveIndex
        AND m.tmNumber IS NOT NULL
    ORDER BY tmNumber
'''
                    message = ''
                    await cursor.execute(query, params)
                    i: int = 0
                    tmNum: int
                    async for name, tmNum in cursor:
                        if message:
                            message += ', '
                        message += f'TM{tmNum:02}: {name}'
                        i += 1
                        if i == 5:
                            yield message
                            message = ''
                            i = 0
                    if message:
                        yield message

                    query = '''
SELECT m.name, m.hmNumber
    FROM gen1_pokemon_tmhmcompatability AS c, gen1_moves AS m
    WHERE c.pokedexNumber=?
        AND c.gameIndex=?
        AND m.gameIndexNumber=c.moveIndex
        AND m.hmNumber IS NOT NULL ORDER BY hmNumber
'''
                    message = ''
                    hmNum: int
                    await cursor.execute(query, params)
                    async for name, hmNum in cursor:
                        if message:
                            message += ', '
                        message += f'HM{hmNum:02}: {name}'
                    if message:
                        yield message
                else:
                    query = '''
SELECT COUNT(*)
    FROM gen1_pokemon_tmhmcompatability AS tmhm
    WHERE pokedexNumber=?
        AND gameIndex=?
        AND (SELECT tmNumber
                FROM gen1_moves
                WHERE gen1_moves.gameIndexNumber=tmhm.moveIndex) IS NOT NULL
'''
                    await cursor.execute(query, params)
                    tmCount: int
                    tmCount, = await cursor.fetchone() or (0,)
                    message = f'Learns {tmCount} TMs'
                    query = '''
SELECT (SELECT name
            FROM gen1_moves
            WHERE gen1_moves.gameIndexNumber=tmhm.moveIndex)
    FROM gen1_pokemon_tmhmcompatability as tmhm
    WHERE pokedexNumber=?
        AND gameIndex=?
        AND (SELECT hmNumber
                FROM gen1_moves
                WHERE gen1_moves.gameIndexNumber=tmhm.moveIndex) IS NOT NULL
'''
                    hms: List[str] = []
                    async for name, in await cursor.execute(query, params):
                        hms.append(name)
                    if hms:
                        message += ', ' + ', '.join(hms)
                    yield message
                return

            moveId: Optional[int] = await self._queryMove()
            if moveId is None:
                yield 'Pokemon or Move Not Found'
                return
            query = '''
SELECT gameIndexNumber, name,
    (SELECT typeName
        FROM gen1_types
        WHERE gen1_types.typeIndex=gen1_moves.typeIndex) AS type,
    basePower, basePP, accuracy, tmNumber, hmNumber
    FROM gen1_moves
    WHERE gameIndexNumber=?
'''
            await cursor.execute(query, (moveId,))
            move: Optional[Tuple[int, str, str, Optional[int], Optional[int],
                                 Optional[int], Optional[int], Optional[int]]]
            move = await cursor.fetchone()
            if move is None:
                yield 'Pokemon or Move Not Found'
                return
            yield f'''\
Move Name: {move[1]}, Move Index: {move[0]}, Type: {move[2]}, \
Base Power: {move[3]}, PP: {move[4]}, Accuracy: {move[5]}'''

            if isFullLearn:
                query = '''
SELECT p.name, l.levelUp
    FROM gen1_pokemon_levelup AS l, gen1_pokemon AS p
    WHERE p.pokedexNumber=l.pokedexNumber AND l.moveIndex=? AND l.gameIndex=?
'''
                params = moveId, gameIds[0],
                async for row in await cursor.execute(query, params):
                    level = '---' if int(row[1]) == 1 else row[1]
                    yield f'{row[0]} learns at {level}'
            else:
                query = '''\
SELECT COUNT(DISTINCT pokedexNumber), levelUp=1
    FROM gen1_pokemon_levelup
    WHERE moveIndex=? AND gameIndex=?
    GROUP BY levelUp=1
    ORDER BY levelUp=1'''
                counts: Dict[bool, int] = {False: 0, True: 0}
                starts: bool
                async for count, starts in await cursor.execute(query, params):
                    counts[starts] = count
                if int(counts[True]) > 0:
                    yield f'{counts[True]} Pokemon starts with this move'
                if int(counts[False]) > 0:
                    yield f'{counts[False]} Pokemon learns this move'

            if move[6] is not None or move[7] is not None:
                item: str
                if move[6] is not None:
                    item = f'TM{move[6]:02}'
                else:
                    item = f'HM{move[7]:02}'
                if isFullTmHm:
                    query = '''
SELECT p.name
    FROM gen1_pokemon_tmhmcompatability AS l, gen1_pokemon AS p
    WHERE p.pokedexNumber=l.pokedexNumber AND l.moveIndex=? AND l.gameIndex=?
'''
                    pokemon: List[str] = []
                    async for name, in await cursor.execute(query, params):
                        length: int
                        length = sum(len(p) + 2 for p in pokemon) + len(name)
                        length += len('These Pokemon learns TM00: ')
                        if length > bot.config.messageLimit:
                            yield (f'These Pokemon learns {item}: '
                                   + ', '.join(pokemon))
                            pokemon.clear()
                        pokemon.append(name)
                    yield f'These Pokemon learns {item}: ' + ', '.join(pokemon)
                else:
                    query = '''
SELECT COUNT(DISTINCT pokedexNumber)
    FROM gen1_pokemon_tmhmcompatability
    WHERE moveIndex=? AND gameIndex=?
'''
                    await cursor.execute(query, params)
                    count, = await cursor.fetchone() or (0,)
                    yield f'{count} Pokemon learns {item}'

    async def pokemonEvolve(self) -> AsyncIterator[str]:
        await self._attachDatabase()
        pokemonId: Optional[int] = await self._queryPokemon()
        if pokemonId is None:
            yield 'Pokemon Not Found'
            return
        cursor: aioodbc.cursor.Cursor
        query: str
        async with await self.database.cursor() as cursor:
            query = '''
SELECT pokedexNumber, name FROM gen1_pokemon WHERE pokedexNumber=?
'''
            await cursor.execute(query, (int(pokemonId),))
            dex: int
            name: str
            dex, name = await cursor.fetchone() or (0, '')
            if not dex:
                yield 'Pokemon Not Found'
                return
            yield f'Pokemon Name: {name}, Pokedex Number: {dex}'
            query = '''
SELECT toPokedexNumber, levelUp, itemIndex, isTrade,
        (SELECT name
            FROM gen1_pokemon
            WHERE gen1_pokemon.pokedexNumber=evo.toPokedexNumber
        ) AS pokemonName,
        (SELECT name
            FROM gen1_items
            WHERE gen1_items.hexIndex=evo.itemIndex) AS itemName
    FROM gen1_pokemon_evolution as evo
    WHERE fromPokedexNumber=?
'''
            await cursor.execute(query, (int(pokemonId),))
            toDex: int
            levelUp: Optional[int]
            item: Optional[int]
            trade: bool
            toName: str
            itemName: Optional[str]
            async for toDex, levelUp, item, trade, toName, itemName in cursor:
                if levelUp:
                    yield f'Evolves to {toName} at level {levelUp}'
                elif item:
                    yield f'Evolves to {toName} with item {itemName}'
                elif trade:
                    yield f'Evolves to {toName} with trading'
            if cursor.rowcount == 0:
                yield f'{name} has no evolutions'

    async def pokemonTmHm(self, isFull: bool) -> AsyncIterator[str]:
        await self._attachDatabase()
        gameIds: Tuple[int, int] = await self._getGameVersionIds()
        moveId: Optional[int] = await self._queryMove()
        if moveId is None:
            yield 'Move Not Found'
            return
        cursor: aioodbc.cursor.Cursor
        query: str
        async with await self.database.cursor() as cursor:
            query = '''
SELECT gameIndexNumber, name,
        (SELECT typeName
            FROM gen1_types
            WHERE gen1_types.typeIndex=gen1_moves.typeIndex) AS type,
        basePower, basePP, accuracy, tmNumber, hmNumber
     FROM gen1_moves
    WHERE gameIndexNumber=?
'''
            await cursor.execute(query, (int(moveId),))
            move: Optional[Tuple[int, str, str, Optional[int], Optional[int],
                                 Optional[int], Optional[int], Optional[int]]]
            move = await cursor.fetchone()
            if move is None or (move[6] is None and move[7] is None):
                yield 'Move Not Found'
                return
            yield '''\
Move Name: {move[1]}, Move Index: {move[0]}, Type: {move[2]}, \
Base Power: {move[3]}, PP: {move[4]}, Accuracy: {move[5]}'''

            item: str
            if move[6] is not None:
                item = f'TM{move[6]:02}'
            else:
                item = f'HM{move[7]:02}'

            params: Tuple[int, int] = (moveId, gameIds[0],)
            if isFull:
                query = '''
SELECT p.name
    FROM gen1_pokemon_tmhmcompatability AS l, gen1_pokemon AS p
    WHERE p.pokedexNumber=l.pokedexNumber AND l.moveIndex=? AND l.gameIndex=?
'''
                pokemon: List[str] = []
                name: str
                async for name, in await cursor.execute(query, params):
                    length: int
                    length = sum(len(p) + 2 for p in pokemon) + len(name)
                    length += len('These Pokemon learns TM00: ')
                    if length > bot.config.messageLimit:
                        yield (f'These Pokemon learns {item}: '
                               + ', '.join(pokemon))
                        pokemon.clear()
                    pokemon.append(name)
                yield f'These Pokemon learns {item}: ' + ', '.join(pokemon)
            else:
                query = '''
SELECT COUNT(DISTINCT pokedexNumber)
    FROM gen1_pokemon_tmhmcompatability
    WHERE moveIndex=? AND gameIndex=?
'''
                await cursor.execute(query, params)
                tmhmCount: int
                tmhmCount, = await cursor.fetchone() or (0,)
                yield f'{tmhmCount} Pokemon learns {item}'

    async def pokemonTm(self, isFull: bool) -> AsyncIterator[str]:
        await self._attachDatabase()
        gameIds: Tuple[int, int] = await self._getGameVersionIds()
        moveId: Optional[int] = await self._queryMove(isTM=True)
        if moveId is None:
            yield 'Move Not Found'
            return
        cursor: aioodbc.cursor.Cursor
        query: str
        async with await self.database.cursor() as cursor:
            query = '''
SELECT gameIndexNumber, name,
        (SELECT typeName
            FROM gen1_types
            WHERE gen1_types.typeIndex=gen1_moves.typeIndex) AS type,
        basePower, basePP, accuracy, tmNumber, hmNumber
    FROM gen1_moves
    WHERE gameIndexNumber=?
'''
            await cursor.execute(query, (int(moveId),))
            move: Optional[Tuple[int, str, str, Optional[int], Optional[int],
                                 Optional[int], Optional[int], Optional[int]]]
            move = await cursor.fetchone()
            if move is None or move[6] is None:
                yield 'Move Not Found'
                return
            yield '''\
Move Name: {move[1]}, Move Index: {move[0]}, Type: {move[2]}, \
Base Power: {move[3]}, PP: {move[4]}, Accuracy: {move[5]}'''

            item: str = f'TM{move[6]:02}'

            params: Tuple[int, int] = (moveId, gameIds[0],)
            if isFull:
                query = '''
SELECT p.name
    FROM gen1_pokemon_tmhmcompatability AS l, gen1_pokemon AS p
    WHERE p.pokedexNumber=l.pokedexNumber AND l.moveIndex=? AND l.gameIndex=?
'''
                pokemon: List[str] = []
                name: str
                async for name, in await cursor.execute(query, params):
                    length: int
                    length = sum(len(p) + 2 for p in pokemon) + len(name)
                    length += len('These Pokemon learns TM00: ')
                    if length > bot.config.messageLimit:
                        yield (f'These Pokemon learns TM{move[6]:02}:'
                               + ', '.join(pokemon))
                        pokemon.clear()
                    pokemon.append(name)
                yield f'These Pokemon learns {item}:' + ', '.join(pokemon)
            else:
                query = '''
SELECT COUNT(DISTINCT pokedexNumber)
    FROM gen1_pokemon_tmhmcompatability
    WHERE moveIndex=? AND gameIndex=?
    '''
                await cursor.execute(query, params)
                tmhmCount: int
                tmhmCount, = await cursor.fetchone() or (0,)
                yield f'{tmhmCount} Pokemon learns {item}'

    async def pokemonHm(self, isFull: bool) -> AsyncIterator[str]:
        await self._attachDatabase()
        gameIds: Tuple[int, int] = await self._getGameVersionIds()
        moveId = await self._queryMove(isTM=True)
        if moveId is None:
            yield 'Move Not Found'
            return
        cursor: aioodbc.cursor.Cursor
        query: str
        async with await self.database.cursor() as cursor:
            query = '''
SELECT gameIndexNumber, name,
        (SELECT typeName
            FROM gen1_types
            WHERE gen1_types.typeIndex=gen1_moves.typeIndex) AS type,
        basePower, basePP, accuracy, tmNumber, hmNumber
    FROM gen1_moves
    WHERE gameIndexNumber=?
'''
            await cursor.execute(query, (int(moveId),))
            move: Optional[Tuple[int, str, str, Optional[int], Optional[int],
                                 Optional[int], Optional[int], Optional[int]]]
            move = await cursor.fetchone()
            if move is None or move[7] is None:
                yield 'Move Not Found'
                return
            yield '''\
Move Name: {move[1]}, Move Index: {move[0]}, Type: {move[2]}, \
Base Power: {move[3]}, PP: {move[4]}, Accuracy: {move[5]}'''

            item: str = f'HM{move[7]:02}'

            params: Tuple[int, int] = (moveId, gameIds[0],)
            if isFull:
                query = '''
SELECT p.name
    FROM gen1_pokemon_tmhmcompatability AS l, gen1_pokemon AS p
    WHERE p.pokedexNumber=l.pokedexNumber AND l.moveIndex=? AND l.gameIndex=?
'''
                pokemon: List[str] = []
                name: str
                async for name, in await cursor.execute(query, params):
                    length: int
                    length = sum(len(p) + 2 for p in pokemon) + len(name)
                    length += len('These Pokemon learns TM00: ')
                    if length > bot.config.messageLimit:
                        yield (f'These Pokemon learns {item}:'
                               + ', '.join(pokemon))
                        pokemon.clear()
                    pokemon.append(name)
                yield f'These Pokemon learns {item}:' + ', '.join(pokemon)
            else:
                query = '''
SELECT COUNT(DISTINCT pokedexNumber)
    FROM gen1_pokemon_tmhmcompatability
    WHERE moveIndex=? AND gameIndex=?
'''
                await cursor.execute(query, params)
                tmhmCount: int
                tmhmCount, = await cursor.fetchone() or (0,)
                yield f'{tmhmCount} Pokemon learns {item}'

    async def pokemonLocation(self, isFull: bool) -> AsyncIterator[str]:
        await self._attachDatabase()
        gameIds: Tuple[int, int] = await self._getGameVersionIds()
        locationId: Optional[int] = await self._queryLocation(gameIds)
        if locationId is None:
            yield 'Location Not Found'
            return
        cursor: aioodbc.cursor.Cursor
        query: str
        async with await self.database.cursor() as cursor:
            query = '''
SELECT mapIndex, name, height, width,
        (SELECT COUNT(*)
            FROM gen1_location_warps AS w
            WHERE w.fromMapIndex=l.mapIndex AND w.versionId=?),
        (SELECT grassEncounterRate
            FROM gen1_location_used AS u
            WHERE u.mapIndex=l.mapIndex AND u.versionId=?),
        (SELECT waterEncounterRate
            FROM gen1_location_used AS u
            WHERE u.mapIndex=l.mapIndex AND u.versionId=?),
        (SELECT COUNT(*)
            FROM gen1_fishing AS f
            WHERE f.locationId=l.mapIndex AND f.versionId=?)
     FROM gen1_locations as l
    WHERE mapIndex=?
'''
            await cursor.execute(query, (gameIds[0],) * 4 + (locationId,))
            location: Optional[Tuple[int, str, int, int, int, Optional[int],
                                     Optional[int], int]]
            location = await cursor.fetchone()
            if location is None:
                yield 'Location Not Found'
                return
            msg: str = f'''\
Location Name: {location[1]}, Index: {location[0]}, Height: {location[2]}, \
Width: {location[3]}, Number of Warps: {location[4]}'''
            if location[5]:
                msg += f', Grass Encounter Rate: {location[5]}/256'
            if location[6]:
                msg += f', Water Encounter Rate: {location[6]}/256'
            if location[7]:
                msg += ', Has Super Rod Fishing'
            yield msg

            encounters: List[str]
            name: str
            minLevel: int
            maxLevel: int
            encRate: int
            level: str
            rate: float

            params: Tuple[int, int] = (gameIds[0], locationId)
            query = '''
SELECT p.name, MIN(w.pokemonLevel), MAX(w.pokemonLevel),
        SUM(CASE WHEN w.slotIndex IN (0, 1) THEN 51
            WHEN w.slotIndex=2 THEN 39
            WHEN w.slotIndex IN (3,4,5) THEN 25
            WHEN w.slotIndex IN (6,7) THEN 13
            WHEN w.slotIndex=8 THEN 11
            WHEN w.slotIndex=9 THEN 3 ELSE 0
            END) as encounterRate
    FROM gen1_wild_encounters AS w, gen1_pokemon AS p
    WHERE w.versionId=? AND w.locationId=? AND w.encounterType='grass'
        AND p.pokedexNumber=w.pokedexNumber
    GROUP BY w.pokedexNumber
    ORDER BY encounterRate DESC
'''
            encounters = []
            await cursor.execute(query, params)
            async for name, minLevel, maxLevel, encRate in cursor:
                if minLevel == maxLevel:
                    level = f'L{minLevel}'
                else:
                    level = 'L{minLevel} - L{maxLevel}'
                rate = round(encRate / 256 * 100, 1)
                encounters.append(f'{name} {level} @ {rate}%')
            if encounters:
                yield 'Grass Encounters: ' + ', '.join(encounters)

            query = '''
SELECT p.name, MIN(w.pokemonLevel), MAX(w.pokemonLevel),
        SUM(CASE WHEN w.slotIndex IN (0, 1) THEN 51
            WHEN w.slotIndex=2 THEN 39
            WHEN w.slotIndex IN (3,4,5) THEN 25
            WHEN w.slotIndex IN (6,7) THEN 13
            WHEN w.slotIndex=8 THEN 11
            WHEN w.slotIndex=9 THEN 3
            ELSE 0
            END) as encounterRate
    FROM gen1_wild_encounters AS w, gen1_pokemon AS p
    WHERE w.versionId=? AND w.locationId=? AND w.encounterType='water'
        AND p.pokedexNumber=w.pokedexNumber
    GROUP BY w.pokedexNumber
    ORDER BY encounterRate DESC
'''
            encounters = []
            await cursor.execute(query, params)
            async for name, minLevel, maxLevel, encRate in cursor:
                if minLevel == maxLevel:
                    level = f'L{minLevel}'
                else:
                    level = 'L{minLevel} - L{maxLevel}'
                rate = round(encRate / 256 * 100, 1)
                encounters.append(f'{name} {level} @ {rate}%')
            if encounters:
                yield 'Water Encounters: ' + ', '.join(encounters)

            query = '''
SELECT p.name, MIN(f.pokemonLevel), MAX(f.pokemonLevel),
        COUNT(slotIndex) as encounterRatio
    FROM gen1_fishing AS f, gen1_pokemon AS p
    WHERE f.versionId=? AND f.locationId=? AND p.pokedexNumber=f.pokedexNumber
    GROUP BY f.pokedexNumber
    ORDER BY encounterRatio DESC
'''
            fishEnc: List[Tuple[str, int, int, int]] = []
            encTotal: int = 0
            await cursor.execute(query, params)
            async for name, minLevel, maxLevel, encRate in cursor:
                fishEnc.append((name, minLevel, maxLevel, encRate))
                encTotal += encRate
            encounters = []
            for name, minLevel, maxLevel, encRate in fishEnc:
                if minLevel == maxLevel:
                    level = f'L{minLevel}'
                else:
                    level = 'L{minLevel} - L{maxLevel}'
                rate = round(encRate / encTotal * 100, 1)
                encounters.append(f'{name} {level} @ {rate}%')
            if encounters:
                yield 'Super Rod Encounters: ' + ', '.join(encounters)

    async def pokemonWild(self, isFull: bool) -> AsyncIterator[str]:
        await self._attachDatabase()
        gameIds: Tuple[int, int] = await self._getGameVersionIds()
        locationId = await self._queryLocation(gameIds)
        if locationId is None:
            yield 'Location Not Found'
            return
        cursor: aioodbc.cursor.Cursor
        query: str
        async with await self.database.cursor() as cursor:
            query = '''
SELECT mapIndex, name,
        (SELECT grassEncounterRate
            FROM gen1_location_used AS u
            WHERE u.mapIndex=l.mapIndex AND u.versionId=?)
    FROM gen1_locations as l
    WHERE mapIndex=?
'''
            params: Tuple[int, int] = (gameIds[0], locationId)
            await cursor.execute(query, params)
            location: Optional[Tuple[int, str, Optional[int]]]
            location = await cursor.fetchone()
            if location is None:
                yield 'Location Not Found'
                return
            msg: str = f'Location Name: {location[1]}, Index: {location[0]}'
            if location[2]:
                msg += f', Grass Encounter Rate: {location[2]}/256'
            yield msg

            query = '''
SELECT p.name, w.pokemonLevel, w.slotIndex
    FROM gen1_wild_encounters AS w, gen1_pokemon AS p
    WHERE w.versionId=? AND w.locationId=? AND w.encounterType='grass'
        AND p.pokedexNumber=w.pokedexNumber
    ORDER BY w.slotIndex ASC
'''
            first: bool = True
            name: str
            level: int
            slot: int
            rate: float
            async for name, level, slot in await cursor.execute(query, params):
                if first:
                    yield 'Grass Encounters:'
                    first = False
                rate = round(_encounterRate256[slot] / 256 * 100, 1)
                yield f'Pokemon: {name}, Level: L{level}, Rate: {rate}%'

    async def pokemonSurf(self, isFull: bool) -> AsyncIterator[str]:
        await self._attachDatabase()
        gameIds: Tuple[int, int] = await self._getGameVersionIds()
        locationId = await self._queryLocation(gameIds)
        if locationId is None:
            yield 'Location Not Found'
            return
        cursor: aioodbc.cursor.Cursor
        query: str
        async with await self.database.cursor() as cursor:
            query = '''
SELECT mapIndex, name,
        (SELECT waterEncounterRate
            FROM gen1_location_used AS u
            WHERE u.mapIndex=l.mapIndex AND u.versionId=?)
    FROM gen1_locations as l
    WHERE mapIndex=?
'''
            params: Tuple[int, int] = (gameIds[0], locationId)
            await cursor.execute(query, params)
            location: Optional[Tuple[int, str, Optional[int]]]
            location = await cursor.fetchone()
            if location is None:
                yield 'Location Not Found'
                return
            msg: str = f'Location Name: {location[1]}, Index: {location[0]}'
            if location[2]:
                msg += f', Water Encounter Rate: {location[2]}/256'
            yield msg

            query = '''
SELECT p.name, w.pokemonLevel, w.slotIndex
    FROM gen1_wild_encounters AS w, gen1_pokemon AS p
    WHERE w.versionId=? AND w.locationId=? AND w.encounterType='water'
        AND p.pokedexNumber=w.pokedexNumber
    ORDER BY w.slotIndex ASC
'''
            first: bool = True
            name: str
            level: int
            slot: int
            rate: float
            async for name, level, slot in await cursor.execute(query, params):
                if first:
                    yield 'Water Encounters:'
                    first = False
                rate = round(_encounterRate256[slot] / 256 * 100, 1)
                yield f'Pokemon: {name}, Level: L{level}, Rate: {rate}%'

    async def pokemonFish(self, isFull: bool) -> AsyncIterator[str]:
        await self._attachDatabase()
        gameIds: Tuple[int, int] = await self._getGameVersionIds()
        locationId = await self._queryLocation(gameIds)
        if locationId is None:
            yield 'Location Not Found'
            return
        cursor: aioodbc.cursor.Cursor
        query: str
        async with await self.database.cursor() as cursor:
            query = '''
SELECT mapIndex, name FROM gen1_locations as l WHERE mapIndex=?
'''
            params: Tuple[int, int] = (gameIds[0], locationId)
            await cursor.execute(query, params)
            location: Optional[Tuple[int, str]]
            location = await cursor.fetchone()
            if location is None:
                yield 'Location Not Found'
                return
            yield f'Location Name: {location[1]}, Index: {location[0]}'
            query = '''
SELECT p.name, f.pokemonLevel, f.slotIndex
    FROM gen1_fishing AS f, gen1_pokemon AS p
    WHERE f.versionId=? AND f.locationId=? AND p.pokedexNumber=f.pokedexNumber
    ORDER BY f.slotIndex ASC
'''
            fishing: List[Tuple[str, int, int]] = []
            encTotal: int = 0
            name: str
            level: int
            slot: int
            async for name, level, slot in await cursor.execute(query, params):
                fishing.append((name, level, slot))
                encTotal += 1
            first: bool = True
            rate: float
            _slot: int
            for name, level, _slot in fishing:
                if first:
                    yield 'Super Rod Encounters:'
                    first = False
                rate = round(1 / encTotal * 100, 1)
                yield f'Pokemon: {name}, Level: L{level}, Rate: {rate}%'

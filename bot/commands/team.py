import re

import discord
from discord import app_commands

from bot.commands.common import (
    ApiPayloadModal,
    ModalField,
    clean_payload,
    execute_api_command,
    optional_positive_int_text,
    optional_season,
    optional_text,
    require_non_negative_int,
    require_payload,
    require_positive_int,
    require_positive_int_text,
    require_season,
    require_text,
    send_validation_error,
)


team_group = app_commands.Group(name='team', description='CRUD operations for team records.')


def _parse_record(value: str | None, *, required: bool) -> dict[str, int]:
    cleaned = optional_text(value)
    if cleaned is None:
        if required:
            return {'wins': 0, 'losses': 0, 'ties': 0}
        return {}

    parts = [part for part in re.split(r'[\s,/-]+', cleaned) if part]
    if len(parts) != 3:
        raise ValueError('Record must use three non-negative integers: wins, losses, ties.')

    try:
        wins_value, losses_value, ties_value = (int(parts[0]), int(parts[1]), int(parts[2]))
    except ValueError as exc:
        raise ValueError('Record must use three non-negative integers: wins, losses, ties.') from exc

    wins, losses, ties = (
        require_non_negative_int(wins_value, 'Wins'),
        require_non_negative_int(losses_value, 'Losses'),
        require_non_negative_int(ties_value, 'Ties'),
    )
    return {'wins': wins, 'losses': losses, 'ties': ties}


@team_group.command(name='list', description='List teams, optionally filtered by game or season.')
async def team_list(interaction: discord.Interaction):
    def build_params(values: dict[str, str]) -> dict[str, object]:
        return clean_payload(
            game_id=optional_positive_int_text(values['game_id'], 'Game ID'),
            season=optional_season(values['season']),
        )

    await interaction.response.send_modal(
        ApiPayloadModal(
            title='List Teams',
            result_title='List Teams',
            method='GET',
            path='/teams',
            fields=[
                ModalField('game_id', 'Game ID filter', 'Positive integer game ID', required=False),
                ModalField('season', 'Season filter', '2025', required=False),
            ],
            payload_builder=build_params,
            payload_target='params',
        )
    )


@team_group.command(name='create', description='Create a team record.')
async def team_create(interaction: discord.Interaction):
    def build_payload(values: dict[str, str]) -> dict[str, object]:
        payload: dict[str, object] = {
            'name': require_text(values['name'], 'Name'),
            'season': require_season(values['season']),
            'game_id': require_positive_int_text(values['game_id'], 'Game ID'),
        }
        payload.update(_parse_record(values['record'], required=True))
        return payload

    await interaction.response.send_modal(
        ApiPayloadModal(
            title='Create Team',
            result_title='Create Team',
            method='POST',
            path='/teams',
            fields=[
                ModalField('name', 'Name'),
                ModalField('season', 'Season', '2025'),
                ModalField('game_id', 'Game ID', 'Positive integer game ID'),
                ModalField('record', 'Record', 'wins, losses, ties - defaults to 0, 0, 0', required=False),
            ],
            payload_builder=build_payload,
        )
    )


@team_group.command(name='get', description='Get a team record by team ID.')
async def team_get(interaction: discord.Interaction, team_id: int):
    try:
        require_positive_int(team_id, 'Team ID')
    except ValueError as exc:
        await send_validation_error(interaction, exc)
        return

    await execute_api_command(interaction, 'Get Team', 'GET', f'/teams/{team_id}')


@team_group.command(name='update', description='Update a team record by team ID.')
async def team_update(interaction: discord.Interaction, team_id: int):
    try:
        require_positive_int(team_id, 'Team ID')
    except ValueError as exc:
        await send_validation_error(interaction, exc)
        return

    def build_payload(values: dict[str, str]) -> dict[str, object]:
        payload = clean_payload(
            name=optional_text(values['name']),
            season=optional_season(values['season']),
            game_id=optional_positive_int_text(values['game_id'], 'Game ID'),
        )
        payload.update(_parse_record(values['record'], required=False))
        require_payload(payload)
        return payload

    await interaction.response.send_modal(
        ApiPayloadModal(
            title='Update Team',
            result_title='Update Team',
            method='PATCH',
            path=f'/teams/{team_id}',
            fields=[
                ModalField('name', 'Name', required=False),
                ModalField('season', 'Season', '2025', required=False),
                ModalField('game_id', 'Game ID', 'Positive integer game ID', required=False),
                ModalField('record', 'Record', 'wins, losses, ties', required=False),
            ],
            payload_builder=build_payload,
        )
    )


@team_group.command(name='delete', description='Delete a team record by team ID.')
async def team_delete(interaction: discord.Interaction, team_id: int):
    try:
        require_positive_int(team_id, 'Team ID')
    except ValueError as exc:
        await send_validation_error(interaction, exc)
        return

    await execute_api_command(interaction, 'Delete Team', 'DELETE', f'/teams/{team_id}')

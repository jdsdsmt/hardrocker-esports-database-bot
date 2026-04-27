import discord
from discord import app_commands

from bot.commands.common import (
    ApiPayloadModal,
    ModalField,
    clean_payload,
    execute_api_command,
    optional_non_negative_int_text,
    optional_positive_int_text,
    require_non_negative_int_text,
    require_payload,
    require_positive_int,
    require_positive_int_text,
    send_validation_error,
)


team_match_group = app_commands.Group(
    name='team-match',
    description='CRUD operations for team-match performance records.',
)


@team_match_group.command(name='list', description='List team-match performance records.')
async def team_match_list(interaction: discord.Interaction):
    def build_params(values: dict[str, str]) -> dict[str, object]:
        return clean_payload(
            team_id=optional_positive_int_text(values['team_id'], 'Team ID'),
            match_id=optional_positive_int_text(values['match_id'], 'Match ID'),
        )

    await interaction.response.send_modal(
        ApiPayloadModal(
            title='List Team Matches',
            result_title='List Team Match Performances',
            method='GET',
            path='/team-match-performances',
            fields=[
                ModalField('team_id', 'Team ID filter', 'Positive integer team ID', required=False),
                ModalField('match_id', 'Match ID filter', 'Positive integer match ID', required=False),
            ],
            payload_builder=build_params,
            payload_target='params',
        )
    )


@team_match_group.command(name='create', description='Create a team-match performance record.')
async def team_match_create(interaction: discord.Interaction):
    def build_payload(values: dict[str, str]) -> dict[str, object]:
        return clean_payload(
            team_id=require_positive_int_text(values['team_id'], 'Team ID'),
            match_id=require_positive_int_text(values['match_id'], 'Match ID'),
            score=optional_non_negative_int_text(values['score'], 'Score'),
        )

    await interaction.response.send_modal(
        ApiPayloadModal(
            title='Create Team Match',
            result_title='Create Team Match Performance',
            method='POST',
            path='/team-match-performances',
            fields=[
                ModalField('team_id', 'Team ID', 'Positive integer team ID'),
                ModalField('match_id', 'Match ID', 'Positive integer match ID'),
                ModalField('score', 'Score', required=False),
            ],
            payload_builder=build_payload,
        )
    )


@team_match_group.command(name='get', description='Get a team-match performance by composite key.')
async def team_match_get(interaction: discord.Interaction, team_id: int, match_id: int):
    try:
        require_positive_int(team_id, 'Team ID')
        require_positive_int(match_id, 'Match ID')
    except ValueError as exc:
        await send_validation_error(interaction, exc)
        return

    await execute_api_command(
        interaction,
        'Get Team Match Performance',
        'GET',
        f'/team-match-performances/{team_id}/{match_id}',
    )


@team_match_group.command(name='update', description='Update a team-match score by composite key.')
async def team_match_update(interaction: discord.Interaction, team_id: int, match_id: int):
    try:
        require_positive_int(team_id, 'Team ID')
        require_positive_int(match_id, 'Match ID')
    except ValueError as exc:
        await send_validation_error(interaction, exc)
        return

    def build_payload(values: dict[str, str]) -> dict[str, object]:
        payload = {'score': require_non_negative_int_text(values['score'], 'Score')}
        require_payload(payload)
        return payload

    await interaction.response.send_modal(
        ApiPayloadModal(
            title='Update Team Match',
            result_title='Update Team Match Performance',
            method='PATCH',
            path=f'/team-match-performances/{team_id}/{match_id}',
            fields=[ModalField('score', 'Score')],
            payload_builder=build_payload,
        )
    )


@team_match_group.command(name='delete', description='Delete a team-match performance by composite key.')
async def team_match_delete(interaction: discord.Interaction, team_id: int, match_id: int):
    try:
        require_positive_int(team_id, 'Team ID')
        require_positive_int(match_id, 'Match ID')
    except ValueError as exc:
        await send_validation_error(interaction, exc)
        return

    await execute_api_command(
        interaction,
        'Delete Team Match Performance',
        'DELETE',
        f'/team-match-performances/{team_id}/{match_id}',
    )

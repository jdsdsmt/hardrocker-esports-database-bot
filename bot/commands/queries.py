import discord
from discord import app_commands

from bot.commands.common import (
    ApiPayloadModal,
    ModalField,
    clean_payload,
    execute_api_command,
    optional_season,
    require_positive_int,
    send_validation_error,
)


query_group = app_commands.Group(name='query', description='Report-style database queries.')


@query_group.command(name='team-members', description='List all members who are part of a team.')
async def query_team_members(interaction: discord.Interaction, team_id: int):
    try:
        require_positive_int(team_id, 'Team ID')
    except ValueError as exc:
        await send_validation_error(interaction, exc)
        return

    await execute_api_command(interaction, 'Team Members', 'GET', f'/teams/{team_id}/members')


@query_group.command(name='senior-members', description='List all members who are seniors.')
async def query_senior_members(interaction: discord.Interaction):
    await execute_api_command(
        interaction,
        'Senior Members',
        'GET',
        '/members',
        params={'academic_year': 'Senior'},
    )


@query_group.command(name='team-matches', description='Retrieve matches that a team has played.')
async def query_team_matches(interaction: discord.Interaction, team_id: int):
    try:
        require_positive_int(team_id, 'Team ID')
    except ValueError as exc:
        await send_validation_error(interaction, exc)
        return

    await execute_api_command(interaction, 'Team Matches', 'GET', f'/teams/{team_id}/matches')


@query_group.command(name='team-record', description='Retrieve a team record for a season.')
async def query_team_record(interaction: discord.Interaction, team_id: int):
    try:
        require_positive_int(team_id, 'Team ID')
    except ValueError as exc:
        await send_validation_error(interaction, exc)
        return

    def build_params(values: dict[str, str]) -> dict[str, object]:
        return clean_payload(season=optional_season(values['season']))

    await interaction.response.send_modal(
        ApiPayloadModal(
            title='Team Record',
            result_title='Team Record',
            method='GET',
            path=f'/teams/{team_id}/record',
            fields=[ModalField('season', 'Season filter', '2025', required=False)],
            payload_builder=build_params,
            payload_target='params',
        )
    )


@query_group.command(name='captain-ids', description='Retrieve student IDs for all captains.')
async def query_captain_ids(interaction: discord.Interaction):
    await execute_api_command(
        interaction,
        'Captain Student IDs',
        'GET',
        '/team-members',
        params={'role': 'Captain', 'fields': 'student_id'},
    )


@query_group.command(name='event-attendees', description='Retrieve students who attended an event.')
async def query_event_attendees(interaction: discord.Interaction, event_id: int):
    try:
        require_positive_int(event_id, 'Event ID')
    except ValueError as exc:
        await send_validation_error(interaction, exc)
        return

    await execute_api_command(interaction, 'Event Attendees', 'GET', f'/events/{event_id}/members')

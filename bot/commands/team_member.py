import discord
from discord import app_commands

from bot.commands.common import (
    TEAM_ROLE_CHOICES,
    ApiPayloadModal,
    ModalField,
    clean_payload,
    execute_api_command,
    optional_choice,
    optional_positive_int_text,
    require_choice,
    require_payload,
    require_positive_int,
    require_positive_int_text,
    send_validation_error,
)


team_member_group = app_commands.Group(
    name='team-member',
    description='CRUD operations for team-member records.',
)


@team_member_group.command(name='list', description='List team-member records.')
async def team_member_list(interaction: discord.Interaction):
    def build_params(values: dict[str, str]) -> dict[str, object]:
        return clean_payload(
            student_id=optional_positive_int_text(values['student_id'], 'Student ID'),
            team_id=optional_positive_int_text(values['team_id'], 'Team ID'),
            role=optional_choice(values['role'], TEAM_ROLE_CHOICES, 'Role'),
        )

    await interaction.response.send_modal(
        ApiPayloadModal(
            title='List Team Members',
            result_title='List Team Members',
            method='GET',
            path='/team-members',
            fields=[
                ModalField('student_id', 'Student ID filter', 'Positive integer student ID', required=False),
                ModalField('team_id', 'Team ID filter', 'Positive integer team ID', required=False),
                ModalField('role', 'Role filter', 'Captain, Coach, Player, or Sub', required=False),
            ],
            payload_builder=build_params,
            payload_target='params',
        )
    )


@team_member_group.command(name='create', description='Create a team-member record.')
async def team_member_create(interaction: discord.Interaction):
    def build_payload(values: dict[str, str]) -> dict[str, object]:
        return {
            'student_id': require_positive_int_text(values['student_id'], 'Student ID'),
            'team_id': require_positive_int_text(values['team_id'], 'Team ID'),
            'role': require_choice(values['role'], TEAM_ROLE_CHOICES, 'Role'),
        }

    await interaction.response.send_modal(
        ApiPayloadModal(
            title='Create Team Member',
            result_title='Create Team Member',
            method='POST',
            path='/team-members',
            fields=[
                ModalField('student_id', 'Student ID', 'Positive integer student ID'),
                ModalField('team_id', 'Team ID', 'Positive integer team ID'),
                ModalField('role', 'Role', 'Captain, Coach, Player, or Sub'),
            ],
            payload_builder=build_payload,
        )
    )


@team_member_group.command(name='get', description='Get a team-member record by composite key.')
async def team_member_get(interaction: discord.Interaction, student_id: int, team_id: int):
    try:
        require_positive_int(student_id, 'Student ID')
        require_positive_int(team_id, 'Team ID')
    except ValueError as exc:
        await send_validation_error(interaction, exc)
        return

    await execute_api_command(
        interaction,
        'Get Team Member',
        'GET',
        f'/team-members/{student_id}/{team_id}',
    )


@team_member_group.command(name='update', description='Update a team-member role by composite key.')
async def team_member_update(interaction: discord.Interaction, student_id: int, team_id: int):
    try:
        require_positive_int(student_id, 'Student ID')
        require_positive_int(team_id, 'Team ID')
    except ValueError as exc:
        await send_validation_error(interaction, exc)
        return

    def build_payload(values: dict[str, str]) -> dict[str, object]:
        payload = {'role': require_choice(values['role'], TEAM_ROLE_CHOICES, 'Role')}
        require_payload(payload)
        return payload

    await interaction.response.send_modal(
        ApiPayloadModal(
            title='Update Team Member',
            result_title='Update Team Member',
            method='PATCH',
            path=f'/team-members/{student_id}/{team_id}',
            fields=[ModalField('role', 'Role', 'Captain, Coach, Player, or Sub')],
            payload_builder=build_payload,
        )
    )


@team_member_group.command(name='delete', description='Delete a team-member record by composite key.')
async def team_member_delete(interaction: discord.Interaction, student_id: int, team_id: int):
    try:
        require_positive_int(student_id, 'Student ID')
        require_positive_int(team_id, 'Team ID')
    except ValueError as exc:
        await send_validation_error(interaction, exc)
        return

    await execute_api_command(
        interaction,
        'Delete Team Member',
        'DELETE',
        f'/team-members/{student_id}/{team_id}',
    )

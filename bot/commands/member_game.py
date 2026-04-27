import discord
from discord import app_commands

from bot.commands.common import (
    ApiPayloadModal,
    ModalField,
    clean_payload,
    execute_api_command,
    optional_text,
    require_payload,
    require_positive_int,
    require_positive_int_text,
    send_validation_error,
)


member_game_group = app_commands.Group(
    name='member-game',
    description='CRUD operations for member-game records.',
)


@member_game_group.command(name='list', description='List member-game records.')
async def member_game_list(interaction: discord.Interaction):
    def build_params(values: dict[str, str]) -> dict[str, object]:
        return clean_payload(
            student_id=require_positive_int_text(values['student_id'], 'Student ID')
            if values['student_id']
            else None,
            game_id=require_positive_int_text(values['game_id'], 'Game ID') if values['game_id'] else None,
        )

    await interaction.response.send_modal(
        ApiPayloadModal(
            title='List Member Games',
            result_title='List Member Games',
            method='GET',
            path='/member-games',
            fields=[
                ModalField('student_id', 'Student ID filter', 'Positive integer student ID', required=False),
                ModalField('game_id', 'Game ID filter', 'Positive integer game ID', required=False),
            ],
            payload_builder=build_params,
            payload_target='params',
        )
    )


@member_game_group.command(name='create', description='Create a member-game record.')
async def member_game_create(interaction: discord.Interaction):
    def build_payload(values: dict[str, str]) -> dict[str, object]:
        return clean_payload(
            student_id=require_positive_int_text(values['student_id'], 'Student ID'),
            game_id=require_positive_int_text(values['game_id'], 'Game ID'),
            username=optional_text(values['username']),
            rank=optional_text(values['rank']),
        )

    await interaction.response.send_modal(
        ApiPayloadModal(
            title='Create Member Game',
            result_title='Create Member Game',
            method='POST',
            path='/member-games',
            fields=[
                ModalField('student_id', 'Student ID', 'Positive integer student ID'),
                ModalField('game_id', 'Game ID', 'Positive integer game ID'),
                ModalField('username', 'Game username', required=False),
                ModalField('rank', 'Rank', required=False),
            ],
            payload_builder=build_payload,
        )
    )


@member_game_group.command(name='get', description='Get a member-game record by composite key.')
async def member_game_get(interaction: discord.Interaction, student_id: int, game_id: int):
    try:
        require_positive_int(student_id, 'Student ID')
        require_positive_int(game_id, 'Game ID')
    except ValueError as exc:
        await send_validation_error(interaction, exc)
        return

    await execute_api_command(
        interaction,
        'Get Member Game',
        'GET',
        f'/member-games/{student_id}/{game_id}',
    )


@member_game_group.command(name='update', description='Update a member-game record by composite key.')
async def member_game_update(interaction: discord.Interaction, student_id: int, game_id: int):
    try:
        require_positive_int(student_id, 'Student ID')
        require_positive_int(game_id, 'Game ID')
    except ValueError as exc:
        await send_validation_error(interaction, exc)
        return

    def build_payload(values: dict[str, str]) -> dict[str, object]:
        payload = clean_payload(username=optional_text(values['username']), rank=optional_text(values['rank']))
        require_payload(payload)
        return payload

    await interaction.response.send_modal(
        ApiPayloadModal(
            title='Update Member Game',
            result_title='Update Member Game',
            method='PATCH',
            path=f'/member-games/{student_id}/{game_id}',
            fields=[
                ModalField('username', 'Game username', required=False),
                ModalField('rank', 'Rank', required=False),
            ],
            payload_builder=build_payload,
        )
    )


@member_game_group.command(name='delete', description='Delete a member-game record by composite key.')
async def member_game_delete(interaction: discord.Interaction, student_id: int, game_id: int):
    try:
        require_positive_int(student_id, 'Student ID')
        require_positive_int(game_id, 'Game ID')
    except ValueError as exc:
        await send_validation_error(interaction, exc)
        return

    await execute_api_command(
        interaction,
        'Delete Member Game',
        'DELETE',
        f'/member-games/{student_id}/{game_id}',
    )

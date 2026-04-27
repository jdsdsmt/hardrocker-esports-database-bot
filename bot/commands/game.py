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
    require_text,
    send_validation_error,
)


game_group = app_commands.Group(name='game', description='CRUD operations for game records.')


@game_group.command(name='list', description='List game records.')
async def game_list(interaction: discord.Interaction):
    await execute_api_command(interaction, 'List Games', 'GET', '/games')


@game_group.command(name='create', description='Create a game record.')
async def game_create(interaction: discord.Interaction):
    def build_payload(values: dict[str, str]) -> dict[str, object]:
        return {
            'name': require_text(values['name'], 'Name'),
            'logo_base64': optional_text(values['logo_base64']) or '',
        }

    await interaction.response.send_modal(
        ApiPayloadModal(
            title='Create Game',
            result_title='Create Game',
            method='POST',
            path='/games',
            fields=[
                ModalField('name', 'Name'),
                ModalField('logo_base64', 'Logo base64', required=False, style=discord.TextStyle.paragraph),
            ],
            payload_builder=build_payload,
        )
    )


@game_group.command(name='get', description='Get a game record by game ID.')
async def game_get(interaction: discord.Interaction, game_id: int):
    try:
        require_positive_int(game_id, 'Game ID')
    except ValueError as exc:
        await send_validation_error(interaction, exc)
        return

    await execute_api_command(interaction, 'Get Game', 'GET', f'/games/{game_id}')


@game_group.command(name='update', description='Update a game record by game ID.')
async def game_update(interaction: discord.Interaction, game_id: int):
    try:
        require_positive_int(game_id, 'Game ID')
    except ValueError as exc:
        await send_validation_error(interaction, exc)
        return

    def build_payload(values: dict[str, str]) -> dict[str, object]:
        payload = clean_payload(
            name=optional_text(values['name']),
            logo_base64=optional_text(values['logo_base64']),
        )
        require_payload(payload)
        return payload

    await interaction.response.send_modal(
        ApiPayloadModal(
            title='Update Game',
            result_title='Update Game',
            method='PATCH',
            path=f'/games/{game_id}',
            fields=[
                ModalField('name', 'Name', required=False),
                ModalField('logo_base64', 'Logo base64', required=False, style=discord.TextStyle.paragraph),
            ],
            payload_builder=build_payload,
        )
    )


@game_group.command(name='delete', description='Delete a game record by game ID.')
async def game_delete(interaction: discord.Interaction, game_id: int):
    try:
        require_positive_int(game_id, 'Game ID')
    except ValueError as exc:
        await send_validation_error(interaction, exc)
        return

    await execute_api_command(interaction, 'Delete Game', 'DELETE', f'/games/{game_id}')

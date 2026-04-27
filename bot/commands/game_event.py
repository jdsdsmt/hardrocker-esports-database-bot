import discord
from discord import app_commands

from bot.commands.common import (
    ApiPayloadModal,
    ModalField,
    clean_payload,
    execute_api_command,
    optional_positive_int_text,
    require_payload,
    require_positive_int,
    require_positive_int_text,
    send_validation_error,
)


game_event_group = app_commands.Group(
    name='game-event',
    description='CRUD operations for game-event records.',
)


@game_event_group.command(name='list', description='List game-event records.')
async def game_event_list(interaction: discord.Interaction):
    def build_params(values: dict[str, str]) -> dict[str, object]:
        return clean_payload(
            game_id=optional_positive_int_text(values['game_id'], 'Game ID'),
            event_id=optional_positive_int_text(values['event_id'], 'Event ID'),
        )

    await interaction.response.send_modal(
        ApiPayloadModal(
            title='List Game Events',
            result_title='List Game Events',
            method='GET',
            path='/game-events',
            fields=[
                ModalField('game_id', 'Game ID filter', 'Positive integer game ID', required=False),
                ModalField('event_id', 'Event ID filter', 'Positive integer event ID', required=False),
            ],
            payload_builder=build_params,
            payload_target='params',
        )
    )


@game_event_group.command(name='create', description='Create a game-event record.')
async def game_event_create(interaction: discord.Interaction):
    def build_payload(values: dict[str, str]) -> dict[str, object]:
        return {
            'game_id': require_positive_int_text(values['game_id'], 'Game ID'),
            'event_id': require_positive_int_text(values['event_id'], 'Event ID'),
        }

    await interaction.response.send_modal(
        ApiPayloadModal(
            title='Create Game Event',
            result_title='Create Game Event',
            method='POST',
            path='/game-events',
            fields=[
                ModalField('game_id', 'Game ID', 'Positive integer game ID'),
                ModalField('event_id', 'Event ID', 'Positive integer event ID'),
            ],
            payload_builder=build_payload,
        )
    )


@game_event_group.command(name='get', description='Get a game-event record by composite key.')
async def game_event_get(interaction: discord.Interaction, game_id: int, event_id: int):
    try:
        require_positive_int(game_id, 'Game ID')
        require_positive_int(event_id, 'Event ID')
    except ValueError as exc:
        await send_validation_error(interaction, exc)
        return

    await execute_api_command(
        interaction,
        'Get Game Event',
        'GET',
        f'/game-events/{game_id}/{event_id}',
    )


@game_event_group.command(name='update', description='Replace a game-event composite key.')
async def game_event_update(interaction: discord.Interaction, game_id: int, event_id: int):
    try:
        require_positive_int(game_id, 'Game ID')
        require_positive_int(event_id, 'Event ID')
    except ValueError as exc:
        await send_validation_error(interaction, exc)
        return

    def build_payload(values: dict[str, str]) -> dict[str, object]:
        payload = clean_payload(
            game_id=optional_positive_int_text(values['game_id'], 'New game ID'),
            event_id=optional_positive_int_text(values['event_id'], 'New event ID'),
        )
        require_payload(payload)
        return payload

    await interaction.response.send_modal(
        ApiPayloadModal(
            title='Update Game Event',
            result_title='Update Game Event',
            method='PATCH',
            path=f'/game-events/{game_id}/{event_id}',
            fields=[
                ModalField('game_id', 'New game ID', 'Positive integer game ID', required=False),
                ModalField('event_id', 'New event ID', 'Positive integer event ID', required=False),
            ],
            payload_builder=build_payload,
        )
    )


@game_event_group.command(name='delete', description='Delete a game-event record by composite key.')
async def game_event_delete(interaction: discord.Interaction, game_id: int, event_id: int):
    try:
        require_positive_int(game_id, 'Game ID')
        require_positive_int(event_id, 'Event ID')
    except ValueError as exc:
        await send_validation_error(interaction, exc)
        return

    await execute_api_command(
        interaction,
        'Delete Game Event',
        'DELETE',
        f'/game-events/{game_id}/{event_id}',
    )

import discord
from discord import app_commands

from bot.commands.common import (
    ApiPayloadModal,
    ModalField,
    clean_payload,
    execute_api_command,
    optional_text,
    require_datetime_text,
    require_payload,
    require_positive_int,
    require_text,
    send_validation_error,
)


event_group = app_commands.Group(name='event', description='CRUD operations for event records.')


@event_group.command(name='list', description='List event records.')
async def event_list(interaction: discord.Interaction):
    def build_params(values: dict[str, str]) -> dict[str, object]:
        return clean_payload(
            starts_after=require_datetime_text(values['starts_after'], 'Starts after')
            if values['starts_after']
            else None,
            starts_before=require_datetime_text(values['starts_before'], 'Starts before')
            if values['starts_before']
            else None,
        )

    await interaction.response.send_modal(
        ApiPayloadModal(
            title='List Events',
            result_title='List Events',
            method='GET',
            path='/events',
            fields=[
                ModalField('starts_after', 'Starts after', '2026-04-10T09:00:00', required=False),
                ModalField('starts_before', 'Starts before', '2026-04-12T18:00:00', required=False),
            ],
            payload_builder=build_params,
            payload_target='params',
        )
    )


@event_group.command(name='create', description='Create an event record.')
async def event_create(interaction: discord.Interaction):
    def build_payload(values: dict[str, str]) -> dict[str, object]:
        return {
            'name': require_text(values['name'], 'Name'),
            'start_time': require_datetime_text(values['start_time'], 'Start time'),
            'end_time': require_datetime_text(values['end_time'], 'End time'),
            'location': require_text(values['location'], 'Location'),
        }

    await interaction.response.send_modal(
        ApiPayloadModal(
            title='Create Event',
            result_title='Create Event',
            method='POST',
            path='/events',
            fields=[
                ModalField('name', 'Name'),
                ModalField('start_time', 'Start time', '2026-04-10T09:00:00'),
                ModalField('end_time', 'End time', '2026-04-10T18:00:00'),
                ModalField('location', 'Location'),
            ],
            payload_builder=build_payload,
        )
    )


@event_group.command(name='get', description='Get an event record by event ID.')
async def event_get(interaction: discord.Interaction, event_id: int):
    try:
        require_positive_int(event_id, 'Event ID')
    except ValueError as exc:
        await send_validation_error(interaction, exc)
        return

    await execute_api_command(interaction, 'Get Event', 'GET', f'/events/{event_id}')


@event_group.command(name='update', description='Update an event record by event ID.')
async def event_update(interaction: discord.Interaction, event_id: int):
    try:
        require_positive_int(event_id, 'Event ID')
    except ValueError as exc:
        await send_validation_error(interaction, exc)
        return

    def build_payload(values: dict[str, str]) -> dict[str, object]:
        payload = clean_payload(
            name=optional_text(values['name']),
            start_time=require_datetime_text(values['start_time'], 'Start time') if values['start_time'] else None,
            end_time=require_datetime_text(values['end_time'], 'End time') if values['end_time'] else None,
            location=optional_text(values['location']),
        )
        require_payload(payload)
        return payload

    await interaction.response.send_modal(
        ApiPayloadModal(
            title='Update Event',
            result_title='Update Event',
            method='PATCH',
            path=f'/events/{event_id}',
            fields=[
                ModalField('name', 'Name', required=False),
                ModalField('start_time', 'Start time', '2026-04-10T09:00:00', required=False),
                ModalField('end_time', 'End time', '2026-04-10T18:00:00', required=False),
                ModalField('location', 'Location', required=False),
            ],
            payload_builder=build_payload,
        )
    )


@event_group.command(name='delete', description='Delete an event record by event ID.')
async def event_delete(interaction: discord.Interaction, event_id: int):
    try:
        require_positive_int(event_id, 'Event ID')
    except ValueError as exc:
        await send_validation_error(interaction, exc)
        return

    await execute_api_command(interaction, 'Delete Event', 'DELETE', f'/events/{event_id}')

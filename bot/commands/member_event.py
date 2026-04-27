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


member_event_group = app_commands.Group(
    name='member-event',
    description='CRUD operations for member-event records.',
)


@member_event_group.command(name='list', description='List member-event records.')
async def member_event_list(interaction: discord.Interaction):
    def build_params(values: dict[str, str]) -> dict[str, object]:
        return clean_payload(
            student_id=optional_positive_int_text(values['student_id'], 'Student ID'),
            event_id=optional_positive_int_text(values['event_id'], 'Event ID'),
        )

    await interaction.response.send_modal(
        ApiPayloadModal(
            title='List Member Events',
            result_title='List Member Events',
            method='GET',
            path='/member-events',
            fields=[
                ModalField('student_id', 'Student ID filter', 'Positive integer student ID', required=False),
                ModalField('event_id', 'Event ID filter', 'Positive integer event ID', required=False),
            ],
            payload_builder=build_params,
            payload_target='params',
        )
    )


@member_event_group.command(name='create', description='Create a member-event record.')
async def member_event_create(interaction: discord.Interaction):
    def build_payload(values: dict[str, str]) -> dict[str, object]:
        return {
            'student_id': require_positive_int_text(values['student_id'], 'Student ID'),
            'event_id': require_positive_int_text(values['event_id'], 'Event ID'),
        }

    await interaction.response.send_modal(
        ApiPayloadModal(
            title='Create Member Event',
            result_title='Create Member Event',
            method='POST',
            path='/member-events',
            fields=[
                ModalField('student_id', 'Student ID', 'Positive integer student ID'),
                ModalField('event_id', 'Event ID', 'Positive integer event ID'),
            ],
            payload_builder=build_payload,
        )
    )


@member_event_group.command(name='get', description='Get a member-event record by composite key.')
async def member_event_get(interaction: discord.Interaction, student_id: int, event_id: int):
    try:
        require_positive_int(student_id, 'Student ID')
        require_positive_int(event_id, 'Event ID')
    except ValueError as exc:
        await send_validation_error(interaction, exc)
        return

    await execute_api_command(
        interaction,
        'Get Member Event',
        'GET',
        f'/member-events/{student_id}/{event_id}',
    )


@member_event_group.command(name='update', description='Replace a member-event composite key.')
async def member_event_update(interaction: discord.Interaction, student_id: int, event_id: int):
    try:
        require_positive_int(student_id, 'Student ID')
        require_positive_int(event_id, 'Event ID')
    except ValueError as exc:
        await send_validation_error(interaction, exc)
        return

    def build_payload(values: dict[str, str]) -> dict[str, object]:
        payload = clean_payload(
            student_id=optional_positive_int_text(values['student_id'], 'New student ID'),
            event_id=optional_positive_int_text(values['event_id'], 'New event ID'),
        )
        require_payload(payload)
        return payload

    await interaction.response.send_modal(
        ApiPayloadModal(
            title='Update Member Event',
            result_title='Update Member Event',
            method='PATCH',
            path=f'/member-events/{student_id}/{event_id}',
            fields=[
                ModalField('student_id', 'New student ID', 'Positive integer student ID', required=False),
                ModalField('event_id', 'New event ID', 'Positive integer event ID', required=False),
            ],
            payload_builder=build_payload,
        )
    )


@member_event_group.command(name='delete', description='Delete a member-event record by composite key.')
async def member_event_delete(interaction: discord.Interaction, student_id: int, event_id: int):
    try:
        require_positive_int(student_id, 'Student ID')
        require_positive_int(event_id, 'Event ID')
    except ValueError as exc:
        await send_validation_error(interaction, exc)
        return

    await execute_api_command(
        interaction,
        'Delete Member Event',
        'DELETE',
        f'/member-events/{student_id}/{event_id}',
    )

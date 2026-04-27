import discord
from discord import app_commands

from bot.commands.common import (
    ApiPayloadModal,
    ModalField,
    clean_payload,
    execute_api_command,
    require_datetime_text,
    require_payload,
    require_positive_int,
    send_validation_error,
)


match_group = app_commands.Group(name='match', description='CRUD operations for match records.')


@match_group.command(name='list', description='List match records.')
async def match_list(interaction: discord.Interaction):
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
            title='List Matches',
            result_title='List Matches',
            method='GET',
            path='/matches',
            fields=[
                ModalField('starts_after', 'Starts after', '2026-04-10T09:00:00', required=False),
                ModalField('starts_before', 'Starts before', '2026-04-12T18:00:00', required=False),
            ],
            payload_builder=build_params,
            payload_target='params',
        )
    )


@match_group.command(name='create', description='Create a match record.')
async def match_create(interaction: discord.Interaction):
    def build_payload(values: dict[str, str]) -> dict[str, object]:
        return {'start_time': require_datetime_text(values['start_time'], 'Start time')}

    await interaction.response.send_modal(
        ApiPayloadModal(
            title='Create Match',
            result_title='Create Match',
            method='POST',
            path='/matches',
            fields=[ModalField('start_time', 'Start time', '2026-04-10T10:00:00')],
            payload_builder=build_payload,
        )
    )


@match_group.command(name='get', description='Get a match record by match ID.')
async def match_get(interaction: discord.Interaction, match_id: int):
    try:
        require_positive_int(match_id, 'Match ID')
    except ValueError as exc:
        await send_validation_error(interaction, exc)
        return

    await execute_api_command(interaction, 'Get Match', 'GET', f'/matches/{match_id}')


@match_group.command(name='update', description='Update a match record by match ID.')
async def match_update(interaction: discord.Interaction, match_id: int):
    try:
        require_positive_int(match_id, 'Match ID')
    except ValueError as exc:
        await send_validation_error(interaction, exc)
        return

    def build_payload(values: dict[str, str]) -> dict[str, object]:
        payload = clean_payload(
            start_time=require_datetime_text(values['start_time'], 'Start time') if values['start_time'] else None,
        )
        require_payload(payload)
        return payload

    await interaction.response.send_modal(
        ApiPayloadModal(
            title='Update Match',
            result_title='Update Match',
            method='PATCH',
            path=f'/matches/{match_id}',
            fields=[ModalField('start_time', 'Start time', '2026-04-10T10:00:00', required=False)],
            payload_builder=build_payload,
        )
    )


@match_group.command(name='delete', description='Delete a match record by match ID.')
async def match_delete(interaction: discord.Interaction, match_id: int):
    try:
        require_positive_int(match_id, 'Match ID')
    except ValueError as exc:
        await send_validation_error(interaction, exc)
        return

    await execute_api_command(interaction, 'Delete Match', 'DELETE', f'/matches/{match_id}')

import discord
from discord import app_commands

from bot.commands.common import (
    ACADEMIC_YEAR_CHOICES,
    ApiPayloadModal,
    ModalField,
    clean_payload,
    execute_api_command,
    optional_choice,
    optional_text,
    require_choice,
    require_payload,
    require_positive_int,
    require_positive_int_text,
    require_text,
    send_validation_error,
)


def _validate_member_email(email: str, first_name: str, last_name: str) -> str:
    cleaned_email = require_text(email, 'Email').lower()
    expected_email = f'{first_name.lower()}.{last_name.lower()}@mines.sdsmt.edu'
    if cleaned_email != expected_email:
        raise ValueError(
            'Email must match firstname.lastname@mines.sdsmt.edu using the provided first and last name.'
        )
    return cleaned_email


member_group = app_commands.Group(name='member', description='CRUD operations for member records.')


@member_group.command(name='list', description='List members, optionally filtered by academic year.')
async def member_list(interaction: discord.Interaction):
    def build_params(values: dict[str, str]) -> dict[str, object]:
        return clean_payload(
            academic_year=optional_choice(values['academic_year'], ACADEMIC_YEAR_CHOICES, 'Academic year'),
        )

    await interaction.response.send_modal(
        ApiPayloadModal(
            title='List Members',
            result_title='List Members',
            method='GET',
            path='/members',
            fields=[
                ModalField(
                    'academic_year',
                    'Academic year filter',
                    'Freshman, Sophomore, Junior, Senior, or Grad',
                    required=False,
                )
            ],
            payload_builder=build_params,
            payload_target='params',
        )
    )


@member_group.command(name='create', description='Create a member record.')
async def member_create(interaction: discord.Interaction):
    def build_payload(values: dict[str, str]) -> dict[str, object]:
        clean_first_name = require_text(values['first_name'], 'First name')
        clean_last_name = require_text(values['last_name'], 'Last name')
        return {
            'student_id': require_positive_int_text(values['student_id'], 'Student ID'),
            'first_name': clean_first_name,
            'last_name': clean_last_name,
            'email_address': _validate_member_email(values['email_address'], clean_first_name, clean_last_name),
            'discord_user_id': str(interaction.user.id),
            'discord_username': interaction.user.name,
            'academic_year': require_choice(values['academic_year'], ACADEMIC_YEAR_CHOICES, 'Academic year'),
        }

    await interaction.response.send_modal(
        ApiPayloadModal(
            title='Create Member',
            result_title='Create Member',
            method='POST',
            path='/members',
            fields=[
                ModalField('student_id', 'Student ID', 'Positive integer student ID'),
                ModalField('first_name', 'First name'),
                ModalField('last_name', 'Last name'),
                ModalField('email_address', 'Email address', 'firstname.lastname@mines.sdsmt.edu'),
                ModalField('academic_year', 'Academic year', 'Freshman, Sophomore, Junior, Senior, or Grad'),
            ],
            payload_builder=build_payload,
        )
    )


@member_group.command(name='get', description='Get a member record by student ID.')
async def member_get(interaction: discord.Interaction, student_id: int):
    try:
        require_positive_int(student_id, 'Student ID')
    except ValueError as exc:
        await send_validation_error(interaction, exc)
        return

    await execute_api_command(interaction, 'Get Member', 'GET', f'/members/{student_id}')


@member_group.command(name='update', description='Update a member record by student ID.')
async def member_update(interaction: discord.Interaction, student_id: int):
    try:
        require_positive_int(student_id, 'Student ID')
    except ValueError as exc:
        await send_validation_error(interaction, exc)
        return

    def build_payload(values: dict[str, str]) -> dict[str, object]:
        clean_first_name = optional_text(values['first_name'])
        clean_last_name = optional_text(values['last_name'])
        clean_email = optional_text(values['email_address'])
        if clean_email and clean_first_name and clean_last_name:
            clean_email = _validate_member_email(clean_email, clean_first_name, clean_last_name)

        payload = clean_payload(
            first_name=clean_first_name,
            last_name=clean_last_name,
            email_address=clean_email,
            academic_year=optional_choice(values['academic_year'], ACADEMIC_YEAR_CHOICES, 'Academic year'),
        )
        require_payload(payload)
        return payload

    await interaction.response.send_modal(
        ApiPayloadModal(
            title='Update Member',
            result_title='Update Member',
            method='PATCH',
            path=f'/members/{student_id}',
            fields=[
                ModalField('first_name', 'First name', required=False),
                ModalField('last_name', 'Last name', required=False),
                ModalField('email_address', 'Email address', 'firstname.lastname@mines.sdsmt.edu', required=False),
                ModalField(
                    'academic_year',
                    'Academic year',
                    'Freshman, Sophomore, Junior, Senior, or Grad',
                    required=False,
                ),
            ],
            payload_builder=build_payload,
        )
    )


@member_group.command(name='delete', description='Delete a member record by student ID.')
async def member_delete(interaction: discord.Interaction, student_id: int):
    try:
        require_positive_int(student_id, 'Student ID')
    except ValueError as exc:
        await send_validation_error(interaction, exc)
        return

    await execute_api_command(interaction, 'Delete Member', 'DELETE', f'/members/{student_id}')

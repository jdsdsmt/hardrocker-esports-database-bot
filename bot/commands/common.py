from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping

import discord

from bot.services.api_client import ApiResult, api_request


ACADEMIC_YEAR_CHOICES = (
    'Freshman',
    'Sophomore',
    'Junior',
    'Senior',
    'Grad',
)

TEAM_ROLE_CHOICES = (
    'Captain',
    'Coach',
    'Player',
    'Sub',
)


@dataclass(frozen=True)
class ModalField:
    key: str
    label: str
    placeholder: str = ''
    required: bool = True
    default: str | None = None
    style: discord.TextStyle = discord.TextStyle.short
    max_length: int | None = None


class ApiPayloadModal(discord.ui.Modal):
    def __init__(
        self,
        *,
        title: str,
        result_title: str,
        method: str,
        path: str,
        fields: Sequence[ModalField],
        payload_builder: Callable[[dict[str, str]], Mapping[str, Any]],
        payload_target: str = 'body',
    ):
        super().__init__(title=title)
        if len(fields) > 5:
            raise ValueError('Discord modals support at most five text inputs.')
        if payload_target not in {'body', 'params'}:
            raise ValueError("payload_target must be either 'body' or 'params'.")

        self.result_title = result_title
        self.method = method
        self.path = path
        self.payload_builder = payload_builder
        self.payload_target = payload_target
        self.inputs: dict[str, discord.ui.TextInput] = {}

        for field in fields:
            text_input_kwargs: dict[str, Any] = {
                'label': field.label,
                'placeholder': field.placeholder,
                'required': field.required,
                'style': field.style,
            }
            if field.default is not None:
                text_input_kwargs['default'] = field.default
            if field.max_length is not None:
                text_input_kwargs['max_length'] = field.max_length

            text_input = discord.ui.TextInput(**text_input_kwargs)
            self.inputs[field.key] = text_input
            self.add_item(text_input)

    async def on_submit(self, interaction: discord.Interaction):
        values = {key: text_input.value for key, text_input in self.inputs.items()}
        try:
            payload = self.payload_builder(values)
        except ValueError as exc:
            await send_validation_error(interaction, exc)
            return

        await execute_api_command(
            interaction,
            self.result_title,
            self.method,
            self.path,
            request_body=payload if self.payload_target == 'body' else None,
            params=payload if self.payload_target == 'params' else None,
        )


def require_positive_int(value: int, field_name: str) -> int:
    if value <= 0:
        raise ValueError(f'{field_name} must be a positive integer.')
    return value


def require_non_negative_int(value: int, field_name: str) -> int:
    if value < 0:
        raise ValueError(f'{field_name} cannot be negative.')
    return value


def require_text(value: str, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f'{field_name} is required.')
    return cleaned


def optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _parse_int(value: str, field_name: str) -> int:
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f'{field_name} must be an integer.') from exc


def require_positive_int_text(value: str, field_name: str) -> int:
    return require_positive_int(_parse_int(require_text(value, field_name), field_name), field_name)


def optional_positive_int_text(value: str | None, field_name: str) -> int | None:
    cleaned = optional_text(value)
    if cleaned is None:
        return None
    return require_positive_int(_parse_int(cleaned, field_name), field_name)


def require_non_negative_int_text(value: str, field_name: str) -> int:
    return require_non_negative_int(_parse_int(require_text(value, field_name), field_name), field_name)


def optional_non_negative_int_text(value: str | None, field_name: str) -> int | None:
    cleaned = optional_text(value)
    if cleaned is None:
        return None
    return require_non_negative_int(_parse_int(cleaned, field_name), field_name)


def require_choice(value: str, choices: Sequence[str], field_name: str) -> str:
    cleaned = require_text(value, field_name)
    choice_by_casefold = {choice.casefold(): choice for choice in choices}
    selected = choice_by_casefold.get(cleaned.casefold())
    if selected is None:
        allowed = ', '.join(choices)
        raise ValueError(f'{field_name} must be one of: {allowed}.')
    return selected


def optional_choice(value: str | None, choices: Sequence[str], field_name: str) -> str | None:
    cleaned = optional_text(value)
    if cleaned is None:
        return None
    return require_choice(cleaned, choices, field_name)


def require_season(value: str) -> str:
    cleaned = require_text(value, 'Season')
    if len(cleaned) != 4 or not cleaned.isdigit():
        raise ValueError('Season must be a four-digit year, for example 2025.')
    return cleaned


def optional_season(value: str | None) -> str | None:
    cleaned = optional_text(value)
    if cleaned is None:
        return None
    return require_season(cleaned)


def require_datetime_text(value: str, field_name: str) -> str:
    cleaned = require_text(value, field_name)
    normalized = cleaned.replace('Z', '+00:00')
    try:
        datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(
            f'{field_name} must be an ISO datetime, for example 2026-04-10T09:00:00.'
        ) from exc
    return cleaned


def clean_payload(**values: Any) -> dict[str, Any]:
    return {key: value for key, value in values.items() if value is not None}


def require_payload(payload: Mapping[str, Any], action: str = 'update') -> None:
    if not payload:
        raise ValueError(f'At least one field is required for {action}.')


def _truncate(value: str, max_length: int = 950) -> str:
    if len(value) <= max_length:
        return value
    return f'{value[: max_length - 15]}\n... truncated'


def _json_text(value: Any) -> str:
    if value is None:
        return '-'
    return json.dumps(value, indent=2, sort_keys=True, default=str)


def _code_block(value: Any) -> str:
    return f'```json\n{_truncate(_json_text(value))}\n```'


def build_api_result_embed(title: str, result: ApiResult) -> discord.Embed:
    if result.configured and result.ok:
        color = discord.Color.green()
        description = 'API request completed.'
    elif result.configured:
        color = discord.Color.red()
        description = 'API request failed.'
    else:
        color = discord.Color.orange()
        description = 'API_BASE_URL is not configured, so this request was not sent.'

    embed = discord.Embed(title=title, description=description, color=color)
    embed.add_field(name='Method', value=result.method, inline=True)
    embed.add_field(name='Endpoint', value=result.path, inline=True)

    if result.status_code is not None:
        embed.add_field(name='Status', value=str(result.status_code), inline=True)

    if result.url:
        embed.add_field(name='URL', value=_truncate(result.url, 1000), inline=False)

    request_details = clean_payload(params=result.params, json=result.request_body)
    embed.add_field(
        name='Request',
        value=_code_block(request_details) if request_details else '-',
        inline=False,
    )

    if result.response_body is not None:
        embed.add_field(name='Response JSON', value=_code_block(result.response_body), inline=False)
    elif result.response_text:
        embed.add_field(name='Response Text', value=_truncate(result.response_text), inline=False)
    elif result.error:
        embed.add_field(name='Error', value=_truncate(result.error), inline=False)

    return embed


async def execute_api_command(
    interaction: discord.Interaction,
    title: str,
    method: str,
    path: str,
    request_body: Mapping[str, Any] | None = None,
    params: Mapping[str, Any] | None = None,
) -> None:
    await interaction.response.defer(ephemeral=True, thinking=True)
    result = await api_request(method, path, request_body=request_body, params=params)
    await interaction.followup.send(embed=build_api_result_embed(title, result), ephemeral=True)


async def send_validation_error(interaction: discord.Interaction, error: Exception) -> None:
    await interaction.response.send_message(str(error), ephemeral=True)

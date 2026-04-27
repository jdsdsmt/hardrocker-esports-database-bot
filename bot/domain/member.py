import re
from typing import Literal, TypedDict, cast

import discord

AcademicYear = Literal['freshman', 'sophomore', 'junior', 'senior', 'grad']
ACADEMIC_YEAR_VALUES = ('freshman', 'sophomore', 'junior', 'senior', 'grad')
ALLOWED_ACADEMIC_YEARS = set(ACADEMIC_YEAR_VALUES)


class MemberPayload(TypedDict):
    student_id: str
    email: str
    first_name: str
    last_name: str
    discord_username: str
    discord_id: int
    academic_year: AcademicYear


class MemberLookupPayload(TypedDict):
    student_id: str
    discord_username: str
    discord_id: int


def require_text(value: str, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f'{field_name} is required.')
    return cleaned


def validate_student_id(student_id: str) -> str:
    cleaned = require_text(student_id, 'Student ID')
    if not re.fullmatch(r'[1-9]\d*', cleaned):
        raise ValueError('Student ID must be a positive integer.')
    return cleaned


def validate_email(email: str, first_name: str, last_name: str) -> str:
    cleaned_email = require_text(email, 'Email').lower()
    expected_email = f'{first_name.lower()}.{last_name.lower()}@mines.sdsmt.edu'
    if cleaned_email != expected_email:
        raise ValueError(
            'Email must match firstname.lastname@mines.sdsmt.edu using the provided first and last name.'
        )
    return cleaned_email


def validate_academic_year(academic_year: str) -> AcademicYear:
    cleaned = require_text(academic_year, 'Academic year').casefold()
    if cleaned not in ALLOWED_ACADEMIC_YEARS:
        raise ValueError('Academic year must be one of: freshman, sophomore, junior, senior, grad.')
    return cast(AcademicYear, cleaned)


def build_member_payload(
    interaction: discord.Interaction,
    student_id: str,
    email: str,
    first_name: str,
    last_name: str,
    academic_year: str,
) -> MemberPayload:
    clean_first_name = require_text(first_name, 'First name')
    clean_last_name = require_text(last_name, 'Last name')
    clean_student_id = validate_student_id(student_id)
    clean_email = validate_email(email, clean_first_name, clean_last_name)
    clean_academic_year = validate_academic_year(academic_year)

    return {
        'student_id': clean_student_id,
        'email': clean_email,
        'first_name': clean_first_name,
        'last_name': clean_last_name,
        'discord_username': interaction.user.name,
        'discord_id': interaction.user.id,
        'academic_year': clean_academic_year,
    }


def build_lookup_payload(interaction: discord.Interaction, student_id: str) -> MemberLookupPayload:
    clean_student_id = validate_student_id(student_id)
    return {
        'student_id': clean_student_id,
        'discord_username': interaction.user.name,
        'discord_id': interaction.user.id,
    }


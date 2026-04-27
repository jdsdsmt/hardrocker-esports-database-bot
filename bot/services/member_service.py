import json
from typing import Mapping


def fetch_member_for_update(student_id: int) -> dict[str, object]:
    """Temporary lookup placeholder until the API is implemented."""
    print(f'FETCH MEMBER FOR UPDATE: student_id={student_id}')
    return {}


def fetch_member_for_get(student_id: int) -> dict[str, object]:
    """Temporary lookup placeholder until the API is implemented."""
    print(f'FETCH MEMBER FOR GET: student_id={student_id}')
    return {}


def log_payload(action: str, payload: Mapping[str, object]) -> None:
    """Temporary service behavior until API integration is added."""
    print(f'MEMBER {action.upper()} PAYLOAD')
    print(json.dumps(dict(payload), indent=2, sort_keys=True))


# Expected API Endpoints

This bot is a Discord client for an API that has not been generated yet. The commands in this repository assume the API exposes the endpoints below. Configure the bot with `API_BASE_URL` when the API exists, for example:

```powershell
$env:API_BASE_URL = "http://localhost:8080/api/v1"
```

If `API_BASE_URL` is not set, the bot logs and displays the request it would have sent.

## Conventions

- Base path: `/api/v1`
- Request and response format: JSON
- Field naming: `snake_case`
- Date/time values: ISO-8601 strings, for example `2026-04-10T09:00:00`
- Successful create: `201 Created` with the created record
- Successful read/update: `200 OK` with the record or list
- Successful delete: `204 No Content`
- Missing record: `404 Not Found`
- Validation or foreign-key error: `400 Bad Request`

## Tables

### MEMBERS

Fields:

| Field | Type | Notes |
| --- | --- | --- |
| `student_id` | integer | Primary key |
| `first_name` | string | Required |
| `last_name` | string | Required |
| `email_address` | string | Required |
| `discord_user_id` | string | Required |
| `discord_username` | string | Required |
| `academic_year` | enum | `Freshman`, `Sophomore`, `Junior`, `Senior`, `Grad` |

Endpoints:

| Method | Path | Parameters | Body |
| --- | --- | --- | --- |
| `GET` | `/members` | Optional query: `academic_year` | None |
| `POST` | `/members` | None | `student_id`, `first_name`, `last_name`, `email_address`, `discord_user_id`, `discord_username`, `academic_year` |
| `GET` | `/members/{student_id}` | `student_id` path integer | None |
| `PATCH` | `/members/{student_id}` | `student_id` path integer | Any mutable member fields |
| `DELETE` | `/members/{student_id}` | `student_id` path integer | None |

### GAME

Fields:

| Field | Type | Notes |
| --- | --- | --- |
| `game_id` | integer | Primary key, auto-increment |
| `name` | string | Required |
| `logo_base64` | string | Base64-encoded content for SQL `Logo` blob |

Endpoints:

| Method | Path | Parameters | Body |
| --- | --- | --- | --- |
| `GET` | `/games` | None | None |
| `POST` | `/games` | None | `name`, `logo_base64` |
| `GET` | `/games/{game_id}` | `game_id` path integer | None |
| `PATCH` | `/games/{game_id}` | `game_id` path integer | `name` and/or `logo_base64` |
| `DELETE` | `/games/{game_id}` | `game_id` path integer | None |

### EVENT

Fields:

| Field | Type | Notes |
| --- | --- | --- |
| `event_id` | integer | Primary key, auto-increment |
| `name` | string | Required |
| `start_time` | datetime | Required |
| `end_time` | datetime | Required |
| `location` | string | Required |

Endpoints:

| Method | Path | Parameters | Body |
| --- | --- | --- | --- |
| `GET` | `/events` | Optional query: `starts_after`, `starts_before` | None |
| `POST` | `/events` | None | `name`, `start_time`, `end_time`, `location` |
| `GET` | `/events/{event_id}` | `event_id` path integer | None |
| `PATCH` | `/events/{event_id}` | `event_id` path integer | Any mutable event fields |
| `DELETE` | `/events/{event_id}` | `event_id` path integer | None |

### MATCHES

Fields:

| Field | Type | Notes |
| --- | --- | --- |
| `match_id` | integer | Primary key, auto-increment |
| `start_time` | datetime | Required |

Endpoints:

| Method | Path | Parameters | Body |
| --- | --- | --- | --- |
| `GET` | `/matches` | Optional query: `starts_after`, `starts_before` | None |
| `POST` | `/matches` | None | `start_time` |
| `GET` | `/matches/{match_id}` | `match_id` path integer | None |
| `PATCH` | `/matches/{match_id}` | `match_id` path integer | `start_time` |
| `DELETE` | `/matches/{match_id}` | `match_id` path integer | None |

### TEAM

Fields:

| Field | Type | Notes |
| --- | --- | --- |
| `team_id` | integer | Primary key, auto-increment |
| `name` | string | Required |
| `wins` | integer | Defaults to `0` |
| `losses` | integer | Defaults to `0` |
| `ties` | integer | Defaults to `0` |
| `season` | string | Four-character season value, for example `2025` |
| `game_id` | integer | Foreign key to `GAME.game_id` |

Endpoints:

| Method | Path | Parameters | Body |
| --- | --- | --- | --- |
| `GET` | `/teams` | Optional query: `game_id`, `season` | None |
| `POST` | `/teams` | None | `name`, `wins`, `losses`, `ties`, `season`, `game_id` |
| `GET` | `/teams/{team_id}` | `team_id` path integer | None |
| `PATCH` | `/teams/{team_id}` | `team_id` path integer | Any mutable team fields |
| `DELETE` | `/teams/{team_id}` | `team_id` path integer | None |

### MEMBER_GAME

Fields:

| Field | Type | Notes |
| --- | --- | --- |
| `student_id` | integer | Composite primary key, foreign key |
| `game_id` | integer | Composite primary key, foreign key |
| `username` | string | Optional |
| `rank` | string | Optional; maps to SQL column ``Rank`` |

Endpoints:

| Method | Path | Parameters | Body |
| --- | --- | --- | --- |
| `GET` | `/member-games` | Optional query: `student_id`, `game_id` | None |
| `POST` | `/member-games` | None | `student_id`, `game_id`, optional `username`, optional `rank` |
| `GET` | `/member-games/{student_id}/{game_id}` | Composite key path | None |
| `PATCH` | `/member-games/{student_id}/{game_id}` | Composite key path | `username` and/or `rank` |
| `DELETE` | `/member-games/{student_id}/{game_id}` | Composite key path | None |

### TEAM_MEMBER

Fields:

| Field | Type | Notes |
| --- | --- | --- |
| `student_id` | integer | Composite primary key, foreign key |
| `team_id` | integer | Composite primary key, foreign key |
| `role` | enum | `Captain`, `Coach`, `Player`, `Sub` |

Endpoints:

| Method | Path | Parameters | Body |
| --- | --- | --- | --- |
| `GET` | `/team-members` | Optional query: `student_id`, `team_id`, `role` | None |
| `POST` | `/team-members` | None | `student_id`, `team_id`, `role` |
| `GET` | `/team-members/{student_id}/{team_id}` | Composite key path | None |
| `PATCH` | `/team-members/{student_id}/{team_id}` | Composite key path | `role` |
| `DELETE` | `/team-members/{student_id}/{team_id}` | Composite key path | None |

### MEMBER_EVENT

Fields:

| Field | Type | Notes |
| --- | --- | --- |
| `student_id` | integer | Composite primary key, foreign key |
| `event_id` | integer | Composite primary key, foreign key |

Endpoints:

| Method | Path | Parameters | Body |
| --- | --- | --- | --- |
| `GET` | `/member-events` | Optional query: `student_id`, `event_id` | None |
| `POST` | `/member-events` | None | `student_id`, `event_id` |
| `GET` | `/member-events/{student_id}/{event_id}` | Composite key path | None |
| `PATCH` | `/member-events/{student_id}/{event_id}` | Composite key path | Optional replacement key fields: `student_id`, `event_id` |
| `DELETE` | `/member-events/{student_id}/{event_id}` | Composite key path | None |

### GAME_EVENT

Fields:

| Field | Type | Notes |
| --- | --- | --- |
| `game_id` | integer | Composite primary key, foreign key |
| `event_id` | integer | Composite primary key, foreign key |

Endpoints:

| Method | Path | Parameters | Body |
| --- | --- | --- | --- |
| `GET` | `/game-events` | Optional query: `game_id`, `event_id` | None |
| `POST` | `/game-events` | None | `game_id`, `event_id` |
| `GET` | `/game-events/{game_id}/{event_id}` | Composite key path | None |
| `PATCH` | `/game-events/{game_id}/{event_id}` | Composite key path | Optional replacement key fields: `game_id`, `event_id` |
| `DELETE` | `/game-events/{game_id}/{event_id}` | Composite key path | None |

### TEAM_MATCH_PERFORMANCE

Fields:

| Field | Type | Notes |
| --- | --- | --- |
| `team_id` | integer | Composite primary key, foreign key |
| `match_id` | integer | Composite primary key, foreign key |
| `score` | integer | Optional |

Endpoints:

| Method | Path | Parameters | Body |
| --- | --- | --- | --- |
| `GET` | `/team-match-performances` | Optional query: `team_id`, `match_id` | None |
| `POST` | `/team-match-performances` | None | `team_id`, `match_id`, optional `score` |
| `GET` | `/team-match-performances/{team_id}/{match_id}` | Composite key path | None |
| `PATCH` | `/team-match-performances/{team_id}/{match_id}` | Composite key path | `score` |
| `DELETE` | `/team-match-performances/{team_id}/{match_id}` | Composite key path | None |

## Query Endpoints

These endpoints cover the required report-style bot commands.

| Query | Method | Path | Parameters | Expected Result |
| --- | --- | --- | --- | --- |
| Members on a team | `GET` | `/teams/{team_id}/members` | `team_id` path integer | Member records with each member's `role` |
| Senior members | `GET` | `/members` | Query: `academic_year=Senior` | Member records where `academic_year` is `Senior` |
| Matches played by a team | `GET` | `/teams/{team_id}/matches` | `team_id` path integer | Match records joined through `TEAM_MATCH_PERFORMANCE`, including `score` |
| Team record in a season | `GET` | `/teams/{team_id}/record` | `team_id` path integer, optional query `season` | `team_id`, `season`, `wins`, `losses`, `ties` |
| Student IDs for captains | `GET` | `/team-members` | Query: `role=Captain&fields=student_id` | Distinct captain `student_id` values |
| Students who attended an event | `GET` | `/events/{event_id}/members` | `event_id` path integer | Member records joined through `MEMBER_EVENT` |

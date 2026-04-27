# Hardrocker Esports Database Bot

This bot uses Discord slash commands to interact with the Hardrocker Esports database API. The API is not generated yet, so the bot can also run in contract-preview mode: if `API_BASE_URL` is not configured, each command logs and displays the exact API request it would send.

The expected API contract is documented in [EXPECTED_API_ENDPOINTS.md](EXPECTED_API_ENDPOINTS.md).

## Configuration

Required:

- `TOKEN`: Discord bot token

Optional until the API exists:

- `API_BASE_URL`: Base URL for the database API, for example `http://localhost:8080/api/v1`

Example `.env`:

```powershell
TOKEN="your-discord-token"
API_BASE_URL="http://localhost:8080/api/v1"
```

## Commands

The bot registers these top-level slash command groups:

- `/member`
- `/game`
- `/event`
- `/match`
- `/team`
- `/member-game`
- `/team-member`
- `/member-event`
- `/game-event`
- `/team-match`
- `/query`
- `/hello`

Each table group supports CRUD-style commands:

- `list`
- `create`
- `get`
- `update`
- `delete`

Slash commands only expose required lookup keys. `list`, `create`, and `update` open Discord modals for filters or editable fields instead of showing optional fields in the command picker.

For composite-key tables, `get`, `update`, and `delete` take both key fields. For pure junction tables such as `member-event` and `game-event`, `update` is treated as replacing the composite key values through a modal.

Team create/update uses one modal field for record values. Enter it as `wins, losses, ties`, for example `5, 2, 0`.

The `/query` group includes:

- `/query team-members`: members assigned to a team
- `/query senior-members`: members whose academic year is `Senior`
- `/query team-matches`: matches a team has played
- `/query team-record`: a team's wins/losses/ties, with optional season entered through a modal
- `/query captain-ids`: student IDs for all captains
- `/query event-attendees`: students who attended an event

## Validation

- IDs must be positive integers.
- Counts and scores cannot be negative.
- `season` must be a four-digit year such as `2025`.
- Datetimes must be ISO-style values such as `2026-04-10T09:00:00`.
- Member academic year is limited to `Freshman`, `Sophomore`, `Junior`, `Senior`, or `Grad`.
- Team member role is limited to `Captain`, `Coach`, `Player`, or `Sub`.
- Member create validates the SDSMT email format from first and last name.

## Project Structure

- `main.py`: bot startup and command registration
- `bot/commands/`: slash command groups
- `bot/commands/common.py`: shared validation and Discord response formatting
- `bot/services/api_client.py`: shared API client and contract-preview behavior
- `EXPECTED_API_ENDPOINTS.md`: expected API endpoint contract generated from the SQL schema

Legacy member-only placeholder modules remain in `bot/domain/` and `bot/services/member_service.py`, but the active commands now use the shared API client.

## Run with Docker

Build the image:

```powershell
docker build -t hardrocker-bot:dev .
```

Run with your Discord token from `.env`:

```powershell
docker run --rm --env-file .env hardrocker-bot:dev
```

Run by passing `TOKEN` directly:

```powershell
docker run --rm -e TOKEN="your-token-here" hardrocker-bot:dev
```

Pass `API_BASE_URL` when the API is available:

```powershell
docker run --rm --env-file .env -e API_BASE_URL="http://host.docker.internal:8080/api/v1" hardrocker-bot:dev
```

See logs from a detached container:

```powershell
docker run -d --name hardrocker-bot --env-file .env hardrocker-bot:dev
docker logs -f hardrocker-bot
```

Stop and remove:

```powershell
docker stop hardrocker-bot
docker rm hardrocker-bot
```

## Run with Docker Compose

Validate compose config:

```powershell
docker compose config
```

Build and start:

```powershell
docker compose up -d --build
```

Follow logs:

```powershell
docker compose logs -f
```

Stop and remove:

```powershell
docker compose down
```

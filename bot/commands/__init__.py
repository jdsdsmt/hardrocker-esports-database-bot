from discord import app_commands

from .event import event_group
from .game import game_group
from .game_event import game_event_group
from .match import match_group
from .member import member_group
from .member_event import member_event_group
from .member_game import member_game_group
from .misc import hello
from .queries import query_group
from .team import team_group
from .team_match import team_match_group
from .team_member import team_member_group


def register_commands(tree: app_commands.CommandTree) -> None:
    tree.add_command(member_group)
    tree.add_command(game_group)
    tree.add_command(event_group)
    tree.add_command(match_group)
    tree.add_command(team_group)
    tree.add_command(member_game_group)
    tree.add_command(team_member_group)
    tree.add_command(member_event_group)
    tree.add_command(game_event_group)
    tree.add_command(team_match_group)
    tree.add_command(query_group)
    tree.add_command(hello)



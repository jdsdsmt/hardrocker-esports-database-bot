import os

import discord
import dotenv
from bot.commands import register_commands
from discord.ext import commands

dotenv.load_dotenv()
intents = discord.Intents.default()

bot = commands.Bot(command_prefix=commands.when_mentioned, intents=intents)


def get_token() -> str:
    token = os.getenv('TOKEN')
    if not token:
        raise RuntimeError(
            'Missing TOKEN environment variable. Pass it with --env-file .env or -e TOKEN=...'
        )
    return token

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


@bot.event
async def setup_hook():
    register_commands(bot.tree)
    synced = await bot.tree.sync()
    print(f'Synced {len(synced)} slash command(s).')


bot.run(get_token())

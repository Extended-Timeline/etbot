from disnake import Message
from disnake.ext.commands import Context

from src.etbot import main


def is_me(ctx: Context | Message): return ctx.author == main.bot.user


def is_not_me(ctx: Context | Message): return not ctx.author == main.bot.user

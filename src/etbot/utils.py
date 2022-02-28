from disnake import Message
from disnake.abc import User
from disnake.ext.commands import Context

import main


def is_me(ctx: Context | Message): return ctx.author == main.bot.user


def user_is_me(usr: User): return usr == main.bot.user


def is_not_me(ctx: Context | Message): return not ctx.author == main.bot.user


def user_is_not_me(usr: User): return not usr == main.bot.user

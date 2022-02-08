from src.etbot import main


def is_me(ctx): return ctx.author == main.bot.user


def is_not_me(ctx): return not ctx.author == main.bot.user

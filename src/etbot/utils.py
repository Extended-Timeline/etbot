from src.etbot import main


def is_me(inter): return inter.author == main.bot.user


def is_not_me(inter): return not inter.author == main.bot.user

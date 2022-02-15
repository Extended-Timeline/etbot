import sys

from disnake.ext import commands

this = sys.modules[__name__]

senator = None


def initialize_testing_roles(bot: commands.Bot):
    this.senator = bot.get_guild(867738868181368852).get_role(867863600973742121)


def initialize_roles(bot: commands.Bot):
    this.senator = bot.get_guild(485360396715425792).get_role(691576535781605417)

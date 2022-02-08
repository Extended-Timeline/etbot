import sys

this = sys.modules[__name__]

senate = None
senatorial_voting = None
staff_bot_commands = None
memes = None


def initialize_testing_channels(bot):
    this.senate = bot.get_channel(867738868181368855)
    this.senatorial_voting = bot.get_channel(867857838142783529)
    this.staff_bot_commands = bot.get_channel(885604958609756190)
    this.memes = bot.get_channel(888136237146337280)


def initialize_channels(bot):
    this.senate = bot.get_channel(694963794757156952)
    this.senatorial_voting = bot.get_channel(698212804808671294)
    this.staff_bot_commands = bot.get_channel(498634929064771605)
    this.memes = bot.get_channel(515253664860995604)

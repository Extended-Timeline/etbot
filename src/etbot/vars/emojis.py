import sys

from disnake.ext import commands

this = sys.modules[__name__]

yes_vote = None
no_vote = None
abstain_vote = None
recycle = None
ear_with_hearing_aid = None
options = [None, None, None, None, None, None]


def initialize_testing_emojis(bot: commands.Bot):
    this.yes_vote = bot.get_emoji(867869297329176587)
    this.no_vote = bot.get_emoji(867869349041799198)
    this.abstain_vote = bot.get_emoji(867869367601070081)
    this.recycle = '♻'
    this.ear_with_hearing_aid = '🦻'
    this.options = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣']


def initialize_emojis(bot: commands.Bot):
    this.yes_vote = bot.get_emoji(698226023795261451)
    this.no_vote = bot.get_emoji(698226052899799130)
    this.abstain_vote = bot.get_emoji(698226077113516118)
    this.recycle = '♻'
    this.ear_with_hearing_aid = '🦻'
    this.options = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣']

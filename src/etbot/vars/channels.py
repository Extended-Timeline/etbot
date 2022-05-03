import sys

from disnake import Thread
from disnake.abc import GuildChannel, PrivateChannel
from disnake.ext import commands

this = sys.modules[__name__]

_bot: commands.Bot | None = None
_senate_id: int | None = None
_senatorial_voting_id: int | None = None
_staff_bot_commands_id: int | None = None
_support_id: int | None = None
_memes_id: int | None = None
_passed_bills_id: int | None = None
_religious_memes_id: int | None = None


def get_senate() -> GuildChannel | Thread | PrivateChannel:
    channel = _bot.get_channel(_senate_id)
    if channel is None:
        raise Exception("#senate not found")
    return channel


def get_senatorial_voting() -> GuildChannel | Thread | PrivateChannel:
    channel = _bot.get_channel(_senatorial_voting_id)
    if channel is None:
        raise Exception("#senatorial-voting not found")
    return channel


def get_staff_bot_commands() -> GuildChannel | Thread | PrivateChannel:
    channel = _bot.get_channel(_staff_bot_commands_id)
    if channel is None:
        raise Exception("#staff-bot-commands not found")
    return channel


def get_support() -> GuildChannel | Thread | PrivateChannel:
    channel = _bot.get_channel(_support_id)
    if channel is None:
        raise Exception("#support not found")
    return channel


def get_memes() -> GuildChannel | Thread | PrivateChannel:
    channel = _bot.get_channel(_memes_id)
    if channel is None:
        raise Exception("#memes not found")
    return channel


def get_passed_bills() -> GuildChannel | Thread | PrivateChannel:
    channel = _bot.get_channel(_passed_bills_id)
    if channel is None:
        raise Exception("#passed-bills not found")
    return channel


def get_religious_memes() -> GuildChannel | Thread | PrivateChannel:
    channel = _bot.get_channel(_religious_memes_id)
    if channel is None:
        raise Exception("#religious-memes not found")
    return channel


# init to set all the values at the start of the bot
def initialize_testing_channels(bot: commands.Bot):
    this._bot = bot
    this._senate_id = 867738868181368855
    this._senatorial_voting_id = 867857838142783529
    this._staff_bot_commands_id = 885604958609756190
    this._memes_id = 888136237146337280
    this._support_id = 941390755971354685
    this._passed_bills_id = 943157076648153089
    this._religious_memes_id = 971105466295935006


def initialize_channels(bot: commands.Bot):
    this._bot = bot
    this._senate_id = 694963794757156952
    this._senatorial_voting_id = 698212804808671294
    this._staff_bot_commands_id = 498634929064771605
    this._memes_id = 515253664860995604
    this._support_id = 504743243226021929
    this._passed_bills_id = 749320980354170972
    this._religious_memes_id = 969724432283234384

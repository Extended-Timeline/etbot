import sys

from disnake import Message

from vars import channels

this = sys.modules[__name__]

_support_id: int | None = None


async def get_support() -> Message:
    return await channels.get_support().fetch_message(_support_id)


def initialize_testing_messages():
    this._support_id = 941391031184818216


def initialize_messages():
    this._support_id = 556837149924917249

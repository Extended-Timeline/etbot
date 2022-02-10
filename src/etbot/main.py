import getopt
import json
import logging
import sys

from disnake.ext import commands

from vars import channels, emojis, roles

logging.basicConfig(level=logging.INFO)

bot = commands.Bot(command_prefix='&')
testing = False


@bot.event
async def on_ready() -> None:
    # must initialize vars after starting bot (especially channels)
    # TODO check if this can be improved with using bot.start()
    if testing:
        channels.initialize_testing_channels(bot)
        emojis.initialize_testing_emojis()
        roles.initialize_testing_roles()
    else:
        channels.initialize_channels(bot)
        emojis.initialize_emojis()
        roles.initialize_roles()

    print(f"Anwesend {bot.user.name}")


def load_extensions() -> None:
    bot.load_extension("cogs.senate")
    bot.load_extension("cogs.meme_voting")


def parse_args(argv: list[str]) -> None:
    try:
        opts, args = getopt.getopt(argv, "ht")
    except getopt.GetoptError:
        print("Invalid argument")
        sys.exit(2)

    global testing

    for opt, arg in opts:
        if opt == 'h':
            print("main.py -h -> Help\n"
                  "main.py -t -> Loads the Testing Channels")
        elif opt == '-t':
            testing = True
            print("Testing...")


def main(argv: list[str] or None = None) -> None:
    if argv:  # TODO check if it works
        parse_args(argv)

    load_extensions()

    with open("token.json", 'r') as token_file:
        token = json.load(token_file)["token"]
    bot.run(token)


if __name__ == "__main__":
    main(sys.argv[1:])

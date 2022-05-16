import datetime
import os
import random

from disnake import Message, Member, User, Guild, Thread, File, NotFound
from disnake.abc import GuildChannel
from disnake.ext import commands

from vars import channels, roles


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Moderation(bot))
    print("Loaded Moderation Cog.")


async def make_message_writeable(message: Message) -> str:
    """
    Makes a message writeable.
    """
    txt: str = f"Author: {message.author.name}#{message.author.discriminator}\n" \
               f"Created at: {message.created_at}\n"

    if message.reference is not None:
        try:
            txt += f"Replying to: {(await message.channel.fetch_message(message.reference.message_id)).clean_content}\n"
        except NotFound:
            txt += f"Replying to: {message.reference.message_id}\n"

    if len(message.attachments) > 0:
        txt += f"Attachments: {message.attachments}\n"
    txt += f"Content: \n" \
           f"{message.clean_content}\n\n\n"

    return txt


async def messages_by_user_in_guild(guild: Guild, user: User | Member) -> int:
    """
    Returns a list of messages sent by a user in a guild.
    """
    counter = 0
    for channel in guild.text_channels:
        counter += await messages_by_user_in_channel(channel, user)

    return counter


async def messages_by_user_in_channel(channel: GuildChannel | Thread, user: User | Member) -> int:
    """
    Returns the number of messages sent by a user in a channel.
    """
    counter = 0
    with open(f"{user.name}.txt", "a", encoding="utf8") as file:
        history = await channel.history(limit=100).flatten()
        for message in history:
            if message.author == user:
                counter += 1
                file.write(f"{message.id}\n{message.created_at}\n{message.clean_content}\n\n\n")
        while not len(history) < 100:
            history = await channel.history(limit=100, before=history[-1]).flatten()
            for message in history:
                if message.author == user:
                    counter += 1
                    file.write(f"{message.id}\n{message.created_at}\n{message.clean_content}\n\n\n")

    return counter


class Moderation(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="save")
    @commands.check(roles.check_is_staff)
    async def save_messages(self, ctx: commands.Context) -> None:
        """
        Saves all messages from a user on a server.
        """
        await ctx.message.delete()

        reference: Message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        user: User | Member = reference.author
        if user is None:
            await ctx.send("User not found.")
            return

        with open(f"transcripts/{user.name}.txt", "w", encoding="utf8") as file:
            file.write(f"{user.name}'s messages as of {datetime.datetime.utcnow()}:\n\n")

        counter = await messages_by_user_in_guild(ctx.guild, user)

        await ctx.send(f"Saved {counter} messages.")

    @commands.command(name="purge")
    @commands.check(roles.check_is_staff)
    async def purge_messages(self, ctx: commands.Context, amount: int) -> None:
        """
        Purges the amount of messages specified.
        """
        await ctx.message.delete()

        channel: GuildChannel | Thread = ctx.channel
        counter = 0
        time = f"{datetime.datetime.utcnow()}"
        filename = f"transcripts/{int(random.randint(0, 10000000))}.txt"

        with open(filename, "w", encoding="utf8") as file:
            file.write(f"{time}:\n\n")
            async for message in channel.history(limit=amount):
                counter += 1
                file.write(await make_message_writeable(message))

        await channel.purge(limit=counter)
        await channels.get_bot_log().send(f"Purged {counter} messages from {ctx.channel.name}.", file=File(filename))
        os.remove(filename)

    @commands.command(name="purgeAfter", aliases=["purgeafter"])
    @commands.check(roles.check_is_staff)
    async def purge_after(self, ctx: commands.Context) -> None:
        """
        Purges all messages after the referenced message.
        """
        await ctx.message.delete()

        channel: GuildChannel | Thread = ctx.channel
        reference: Message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        counter = 0
        time = f"{datetime.datetime.utcnow()}"
        filename = f"transcripts/{int(random.randint(0, 10000000))}.txt"

        with open(filename, "w", encoding="utf8") as file:
            file.write(f"{time}:\n\n")

            history = await channel.history(limit=100, after=reference).flatten()
            for message in history:
                counter += 1
                file.write(await make_message_writeable(message))

            while not len(history) < 100:
                history = await channel.history(limit=100, before=history[-1], after=reference).flatten()
                for message in history:
                    counter += 1
                    file.write(await make_message_writeable(message))

        await channel.purge(limit=counter, after=reference)
        await channels.get_bot_log().send(f"Purged {counter} messages from {ctx.channel.name}.", file=File(filename))
        os.remove(filename)

    @commands.command(name="purgeBefore", aliases=["purgebefore"])
    @commands.check(roles.check_is_staff)
    async def purge_before(self, ctx: commands.Context, amount: int) -> None:
        """
        Purges the amount of messages specified before the referenced message.
        """
        await ctx.message.delete()

        channel: GuildChannel | Thread = ctx.channel
        reference: Message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        counter = 0
        time = f"{datetime.datetime.utcnow()}"
        filename = f"transcripts/{int(random.randint(0, 10000000))}.txt"

        with open(filename, "w", encoding="utf8") as file:
            file.write(f"{time}:\n\n")

            async for message in channel.history(limit=amount, before=reference):
                counter += 1
                file.write(await make_message_writeable(message))

        await channel.purge(limit=counter, before=reference)
        await channels.get_bot_log().send(f"Purged {counter} messages from {ctx.channel.name}.", file=File(filename))
        os.remove(filename)

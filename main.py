import sys
import discord

from discord.ext import commands

from groupcog import Group
from statuscog import Status
from tracker import Tracker

if __name__ == '__main__':
    intents = discord.Intents.default()
    intents.reactions = True

    bot = commands.Bot(command_prefix='!', intents=intents)

    tracker = Tracker(max_group_size=5, loot_per_run=1)

    channel = "general"


    @bot.check
    async def globally_require_channel(ctx):
        return ctx.channel.name == channel


    @bot.check
    async def globally_require_guild(ctx):
        return ctx.guild.id == 777286602166239254


    @bot.event
    async def on_ready():
        print('We have logged in as %s' % bot.user)


    @bot.event
    async def on_member_join(member):
        ch = member.guild.system_channel
        if ch is not None:
            await ch.send('Welcome %s! Type !help to get started.' % member)


    bot.add_cog(Status(tracker))
    bot.add_cog(Group(tracker, bot))

    bot.run(sys.argv[1])

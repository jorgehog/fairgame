import sys
import discord
import threading
import time

from discord.ext import commands

from config import Config
from groupcog import Group
from memberinfo import MemberInfo
from statuscog import Status
from tracker import Tracker

if __name__ == '__main__':
    intents = discord.Intents.default()
    intents.reactions = True
    intents.members = True

    member_info = {}
    try:
        with open(Config.persistence_file, 'r') as f:
            for line in f:
                user_id, display_name, balance = line.split()
                member_info[int(user_id)] = MemberInfo(display_name, int(balance))
    except FileNotFoundError:
        pass

    bot = commands.Bot(command_prefix='!', intents=intents)

    tracker = Tracker(member_info, max_group_size=Config.max_group_size, loot_per_run=Config.loot_per_run)

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


    def persist_member_info():
        while True:
            time.sleep(Config.persistence_interval)

            if tracker.member_info:
                with open(Config.persistence_file, 'w') as f:
                    for user_id, info in tracker.member_info.items():
                        f.write('%d %s %s\n' % (user_id, info.display_name, info.balance))


    thread = threading.Thread(target=persist_member_info)
    thread.start()

    bot.run(sys.argv[1])

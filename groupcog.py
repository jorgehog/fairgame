import re

from config import Config
from discord.ext import commands


class Group(commands.Cog):
    def __init__(self, tracker, bot):
        self.tracker = tracker
        self.bot = bot

    @staticmethod
    def is_group_message(msg, suffix):
        res = re.findall('Group (\d+)%s' % suffix, msg)
        if res:
            return int(res[0])
        else:
            return

    @commands.command(name='create', help='Creates a new group.')
    async def create(self, ctx):
        self.tracker.start_trace()
        group_id = self.tracker.create(ctx.author)
        res = self.tracker.end_trace()
        if group_id:
            self.tracker.join(ctx.author, group_id)

        await ctx.send("```%s```" % '\n'.join(res))

    @commands.command(name='disband', help='Disband your current group')
    async def disband(self, ctx):
        self.tracker.start_trace()
        self.tracker.disband_group(ctx.author)

        await ctx.send("```%s```" % '\n'.join(self.tracker.end_trace()))

    @commands.command(name='done', help='Register a run as complete.')
    async def complete_run(self, ctx):
        self.tracker.start_trace()
        self.tracker.complete_run(ctx.author)

        await ctx.send("```%s```" % '\n'.join(self.tracker.end_trace()))

    @commands.command(name='plan', help='Calculate the most optimal plan for your group')
    async def make_plan(self, ctx, _count: int = 5):
        count = min(_count, 10)

        maybe_group = self.tracker.group_of(ctx.author)
        member_stats = self.tracker.stats_for_group(maybe_group) if maybe_group else None

        if member_stats:
            copied = sorted([m.copy() for m in member_stats], key=lambda k: k.balance)
            reports = ['Current status: %s' % " | ".join([c.report() for c in copied])]

            run = 1
            while run <= count:
                looter = copied[-1]
                before = looter.report_verbose()

                for member in copied[:-1]:
                    member.balance += 1
                    looter.balance -= 1

                copied = sorted(copied, key=lambda k: k.balance)

                after = " | ".join([c.report() for c in copied])

                reports.append('>Looter %d:      %s\nUpdated status: %s' % (run, before, after))

                run += 1

            await ctx.send("```%s```" % '\n\n'.join(reports))
        else:
            await ctx.send("```%s```" % Config.no_group_reply)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.name != 'fairgame':
            group_message = self.is_group_message(reaction.message.content, ' created')
            if group_message and reaction.emoji == Config.join_group_emoji:
                self.tracker.join(user, group_message)
            else:
                group_id = self.is_group_message(reaction.message.content, ' run completed!')
                if group_id and reaction.emoji in Config.index_emojis:
                    index = Config.index_emojis.index(reaction.emoji)

                    if index < self.tracker.loot_per_run:
                        message_id = reaction.message.id

                        for group in self.tracker.group_map.values():
                            if group.loot_message_id == message_id and user.id in group.members:
                                looter = self.tracker.member_info[user.id]

                                for member_id in group.members:
                                    if member_id != user.id:
                                        booster = self.tracker.member_info[member_id]

                                        booster.balance -= 1
                                        looter.balance += 1

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, event):
        if event.emoji.name == Config.join_group_emoji:
            for group in self.tracker.group_map.values():
                if group.invite_message_id == event.message_id:
                    self.tracker._leave(event.user_id)
                    break

        elif event.emoji.name in Config.index_emojis:
            index = Config.index_emojis.index(event.emoji.name)

            if index < self.tracker.loot_per_run:
                for group in self.tracker.group_map.values():
                    if group.loot_message_id == event.message_id and event.user_id in group.members:
                        looter = self.tracker.member_info[event.user_id]

                        for member_id in group.members:
                            if member_id != event.user_id:
                                booster = self.tracker.member_info[member_id]

                                booster.balance -= 1
                                looter.balance += 1

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.name == Config.bot_user:
            group_id = self.is_group_message(message.content, ' created')
            if group_id:
                self.tracker.register_group_invite_message(group_id, message.id)
                await message.add_reaction(Config.join_group_emoji)
            else:
                group_id = self.is_group_message(message.content, ' run completed!')
                if group_id:
                    self.tracker.register_group_loot_message(group_id, message.id)

                    n = self.tracker.loot_per_run
                    for emoji in Config.index_emojis[:n]:
                        await message.add_reaction(emoji)

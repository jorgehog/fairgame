import typing, re

from discord.ext import commands


class Group(commands.Cog):
    def __init__(self, tracker, bot):
        self.tracker = tracker
        self.bot = bot

    @staticmethod
    def is_group_message(msg):
        res = re.findall('New group (\d+) created', msg)
        if res:
            return int(res[0])
        else:
            return

    # @commands.command(name='join', help='Joins the last created group or a specific group')
    # async def join(self, ctx, group_id: typing.Optional[int] = None):
    #     self.tracker.start_trace()
    #     self.tracker.join(ctx.author, group_id or self.tracker.max_group_id())
    #
    #     await ctx.send("```%s```" % '\n'.join(self.tracker.end_trace()))

    @commands.command(name='create', help='Creates a new group.')
    async def create(self, ctx):
        self.tracker.start_trace()
        group_id = self.tracker.create(ctx.author)
        if group_id:
            self.tracker.join(ctx.author, group_id)

        await ctx.send("```%s```" % '\n'.join(self.tracker.end_trace()))

    # @commands.command(name='leave', help='Leave your current group')
    # async def leave(self, ctx):
    #     self.tracker.start_trace()
    #     self.tracker.leave(ctx.author)
    #
    #     await ctx.send("```%s```" % '\n'.join(self.tracker.end_trace()))

    @commands.command(name='disband', help='Disband your current group')
    async def disband(self, ctx):
        self.tracker.start_trace()
        self.tracker.disband_group(ctx.author)

        await ctx.send("```%s```" % '\n'.join(self.tracker.end_trace()))

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.name != 'fairgame':
            res = self.is_group_message(reaction.message.content)
            if res:
                self.tracker.join(user, res)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, event):
        self.tracker._leave(event.user_id)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.name == 'fairgame' and self.is_group_message(message.content):
            await message.add_reaction('\U0001F44D')

    @commands.command(name='plan', help='Calculate the most optimal plan for your group')
    async def make_plan(self, ctx, _count: int = 5):
        count = min(_count, 10)

        maybe_group = self.tracker.group_of(ctx.author)
        member_stats = self.tracker.stats_for_group(maybe_group) if maybe_group else None

        if member_stats:
            copied = sorted([m.copy() for m in member_stats], key=lambda k: k.diff())
            reports = []

            run = 1
            while run <= count:
                looter = copied[-1]
                before = looter.report()

                for member in copied:
                    member.start_run()
                looter.register_looter()

                copied = sorted(copied, key=lambda k: k.diff())

                after = " | ".join(["%s (%d)" % (c.display_name, c.diff()) for c in copied])

                reports.append("Run #%d:\nBefore: %s\nAfter:  %s" % (run, before, after))

                run += 1

            await ctx.send("```%s```" % '\n\n'.join(reports))
        else:
            await ctx.send("```%s```" % 'You are not part of a group.')

    # @commands.command(name='history', help='Show the history of your group')
    # async def history(self, ctx):
    #     maybe_group = self.tracker.group_of(ctx.author)
    #
    #     if maybe_group:
    #         group = self.tracker.group_map[maybe_group]
    #         if group.history:
    #             res = '%d runs. Winners: %s.' % (group.completed_runs, ', '.join(group.history))
    #         else:
    #             res = 'No history.'
    #     else:
    #         res = 'You are not part of a group.'
    #
    #     await ctx.send("```%s```" % res)

    @commands.command(name='start', help='Register a run as started')
    async def start_run(self, ctx):
        self.tracker.start_trace()
        if self.tracker.start_run(ctx.author):
            self.tracker.end_trace()
            await self.bot.get_cog('Status').group_status(ctx)
        else:
            await ctx.send("```%s```" % '\n'.join(self.tracker.end_trace()))

    @commands.command(name='loot', help='Register yourself as the chosen looter')
    async def register_looter(self, ctx):
        self.tracker.start_trace()
        if self.tracker.register_looter(ctx.author):
            self.tracker.end_trace()
            await self.bot.get_cog('Status').group_status(ctx)
        else:
            await ctx.send("```%s```" % '\n'.join(self.tracker.end_trace()))

from discord.ext import commands


class Status(commands.Cog):
    def __init__(self, tracker):
        self.tracker = tracker

    @commands.command(name='me', help='Show your status')
    async def member_status(self, ctx):
        res = self.tracker.member_status(ctx.author)

        await ctx.send("```%s```" % (res if res else 'No runs completed!'))

    @commands.command(name='group', help='Show the status of your group')
    async def group_status(self, ctx):
        maybe_group = self.tracker.group_of(ctx.author)

        if maybe_group:
            res = self.tracker.group_status(maybe_group)
            await ctx.send("```Group %d\n%s```" % (maybe_group, '\n'.join(res)))
        else:
            await ctx.send("```%s```" % 'You are not part of a group')

    @commands.command(name='status', help='Show the status of all members')
    async def status(self, ctx):
        res = '\n'.join(self.tracker.status())
        await ctx.send("```%s```" % (res if res else 'No runs completed!'))

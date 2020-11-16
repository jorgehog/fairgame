import discord

from config import Config
from memberinfo import MemberInfo
from groupinfo import GroupInfo


class Tracker:
    def __init__(self, member_info, max_group_size: int, loot_per_run: int):
        self.max_group_size = max_group_size
        self.loot_per_run = loot_per_run

        self.member_info = member_info
        self.group_map = {}
        self._logger = None

    def start_trace(self):
        self._logger = []

    def end_trace(self):
        trace = self._logger
        self._logger = None
        return trace if trace else ['-']

    def _log(self, message):
        if self._logger is not None:
            self._logger.append(message)

    def max_group_id(self):
        if self.group_map:
            return max(self.group_map.keys())
        else:
            return 0

    def _group_of(self, member_ref: int):
        if member_ref in self.member_info:
            return self.member_info[member_ref].group_id
        else:
            return

    def group_of(self, member: discord.Member):
        return self._group_of(member.id)

    def stats_for_group(self, group_id):
        maybe_group = self.group_map.get(group_id)

        if maybe_group:
            return [self.member_info[member] for member in maybe_group.members]
        else:
            return []

    def _get_or_create(self, member_ref: int, display_name: str):
        if member_ref not in self.member_info:
            self.member_info[member_ref] = MemberInfo(display_name)
            self._log('New entry for %s created.' % display_name)

        return self.member_info[member_ref]

    def join(self, member: discord.Member, group_id: int):
        member_ref = member.id
        info = self._get_or_create(member_ref, member.display_name)
        if not info.group_id:
            if group_id in self.group_map:
                info.group_id = group_id

                if len(self.group_map[group_id].members) < self.max_group_size:
                    self.group_map[group_id].add_member(member_ref)
                    self._log('%s joined group %d.' % (member.display_name, group_id))
                else:
                    self._log('Group %d is full.' % group_id)
            else:
                self._log('Group %d does not exist.' % group_id)

        else:
            self._log('%s is already part of group %s.' % (member.display_name, info.group_id))

    def create(self, member: discord.Member):
        next_group_id = self.max_group_id() + 1
        maybe_group = self.group_of(member)
        if not maybe_group:
            self.group_map[next_group_id] = GroupInfo(self.loot_per_run)
            self._log(
                'Group %d created by %s. React with %s to join them. !run once you\'re ready.' % (
                    next_group_id, member.display_name, Config.join_group_emoji))
            return next_group_id
        else:
            self._log('%s is already part of group %s.' % (member.display_name, maybe_group))
            return

    def _is_leader(self, member_ref):
        maybe_group = self._group_of(member_ref)

        if maybe_group:
            return self.group_map[maybe_group].leader() == member_ref
        else:
            return False

    def is_leader(self, member: discord.Member):
        return self._is_leader(member.id)

    def _leave(self, member_ref: int):
        if member_ref in self.member_info:
            info = self.member_info[member_ref]

            if info.group_id:
                self.group_map[info.group_id].remove_member(member_ref)
                self._log('%s left group %d.' % (info.display_name, info.group_id))

                if len(self.group_map[info.group_id].members) == 0:
                    self._log('Group %d disbanded.' % info.group_id)
                    del self.group_map[info.group_id]

                info.group_id = None

    def leave(self, member: discord.Member):
        self._leave(member.id)

    def disband_group(self, member: discord.Member):
        member_ref = member.id
        if self._is_leader(member_ref):
            to_leave = [ref for ref in self.group_map[self.member_info[member_ref].group_id].members]
            for group_member_ref in to_leave:
                self._leave(group_member_ref)

        else:
            self._log('Only group leaders can disband groups.')

    def start_run(self, member: discord.Member):
        member_ref = member.id
        if self._is_leader(member_ref):
            group_id = self.member_info[member_ref].group_id
            group_info = self.group_map[group_id]

            group_members = [self.member_info[group_member_ref] for group_member_ref in group_info.members]

            suggested_looter = max(group_members, key=lambda x: x.balance)

            react_string = '/'.join(Config.index_emojis[:self.loot_per_run])

            self._log(
                'Group %d run started! React %s if you are looting %s.\nBased on point balance we suggest %s (points = %d).' % (
                    group_id, react_string, Config.loot_string, suggested_looter.display_name,
                    suggested_looter.balance))

        else:
            self._log('Only group leaders can complete runs.')

    def member_status(self, member: discord.Member):
        member_ref = member.id
        if member_ref in self.member_info:
            self.member_info[member_ref].display_name = member.display_name  # Update member name
            return self.member_info[member_ref].report_verbose()
        else:
            return

    def group_status(self, group_id: int):
        return [info.report_verbose() for info in self.stats_for_group(group_id)]

    def status(self):
        return [info.report_verbose() for info in sorted(self.member_info.values(), key=lambda info: info.display_name)]

    def register_group_loot_message(self, group_id, message_id):
        self.group_map[group_id].loot_message_id = message_id

    def register_group_invite_message(self, group_id, message_id):
        self.group_map[group_id].invite_message_id = message_id

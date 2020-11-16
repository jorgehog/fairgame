class GroupInfo:
    def __init__(self, loot_per_run):
        self.members = []
        self.loot_per_run = loot_per_run

        self.looters = 0

        self.invite_message_id = None
        self.loot_message_id = None

    def leader(self):
        return self.members[0] if self.members else None

    def add_member(self, member):
        self.members.append(member)

    def remove_member(self, member):
        self.members.remove(member)

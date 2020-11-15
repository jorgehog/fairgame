class GroupInfo:
    def __init__(self, loot_per_run):
        self.members = []
        self.loot_per_run = loot_per_run

        self.started_runs = 0

        self.history = []

    def leader(self):
        return self.members[0] if self.members else None

    def start_run(self):
        self.started_runs += 1

    def register_looter(self, looter):
        self.history.append(looter)

    def times_looted(self):
        return len(self.history)

    def has_unclaimed_loot(self):
        return self.times_looted() * self.loot_per_run < self.started_runs

    def add_member(self, member):
        self.members.append(member)

    def remove_member(self, member):
        self.members.remove(member)

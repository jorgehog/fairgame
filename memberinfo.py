class MemberInfo:
    def __init__(self, display_name: str, max_group_size: int, runs: int = 0, loot_runs: int = 0):
        self.display_name = display_name
        self.max_group_size = max_group_size
        self.runs = runs
        self.loot_runs = loot_runs
        self.group_id = None

    def register_looter(self):
        self.loot_runs += 1

    def start_run(self):
        self.runs += 1

    def diff(self):
        return self.runs - self.loot_runs * self.max_group_size

    def report(self):
        name = self.display_name.ljust(20)
        return "%s %3d run balance (%3d runs, looted %d times)" % (name, self.diff(), self.runs, self.loot_runs)

    def copy(self):
        return MemberInfo(self.display_name, self.max_group_size, self.runs, self.loot_runs)

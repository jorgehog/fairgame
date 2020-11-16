class MemberInfo:
    def __init__(self, display_name: str, max_group_size: int, runs: int = 0, times_looted: int = 0):
        self.display_name = display_name
        self.max_group_size = max_group_size
        self.runs = runs
        self.times_looted = times_looted
        self.group_id = None

    def diff(self):
        return self.runs - self.times_looted * self.max_group_size # Todo: Dynamic grp size

    def report(self):
        name = self.display_name.ljust(20)
        return "%s %3d run balance (%3d runs, looted %d times)" % (name, self.diff(), self.runs, self.times_looted)

    def copy(self):
        return MemberInfo(self.display_name, self.max_group_size, self.runs, self.times_looted)

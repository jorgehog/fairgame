class MemberInfo:
    def __init__(self, display_name: str, balance: int = 0):
        self.display_name = display_name
        self.balance = balance
        self.group_id = None

    def report(self):
        return '%-10s %2d' % (self.display_name, self.balance)

    def report_verbose(self):
        if self.balance == 0:
            explanation = 'neutral'
        elif self.balance < 0:
            plural = 's' if self.balance < -1 else ''
            explanation = 'owes %d run%s' % (-self.balance, plural)
        else:
            plural = 's' if self.balance > 1 else ''
            explanation = 'is owed help from %d player%s' % (self.balance, plural)

        return "%s (%s)" % (self.report(), explanation)

    def copy(self):
        return MemberInfo(self.display_name, self.balance)

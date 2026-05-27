from enum import Enum

class GoalScope(Enum):
    PORTFOLIO = "portfolio"
    ACCOUNT = "account"

class GoalPeriod(Enum):
    TOTAL = "total"
    ANNUAL = "annual"
    MONTHLY = "monthly"

class Goal:
    def __init__(
            self, 
            id, 
            target_amount, 
            deadline, 
            scope: GoalScope, 
            period: GoalPeriod, 
            account_id=None
    ):
        self.id = id
        self.target_amount = target_amount
        self.deadline = deadline
        self.scope = scope
        self.period = period
        self.account_id = account_id

    @property
    def name(self):
        return f"{self.scope.value.capitalize()} {self.period}"
    
    @classmethod
    def from_row(cls, row):
        # Converts a database row (tuple) into an Account object
        return cls(
            id = row[0],
            target_amount = row[1],
            deadline = row[2],
            scope = GoalScope(row[3]),
            period = GoalPeriod(row[4]),
            account_id = row[5]
        )

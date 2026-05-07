class Wallet:
    """Represents a user's internal energy trading wallet."""

    def __init__(self, user_id: str, balance: float = 0.0):
        self.user_id = user_id
        self.balance = balance

    def debit(self, amount: float):
        if self.balance < amount:
            raise ValueError(f"Insufficient funds. Balance: {self.balance}, Required: {amount}")
        self.balance -= amount
        self.balance = round(self.balance, 2)

    def credit(self, amount: float):
        self.balance += amount
        self.balance = round(self.balance, 2)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "balance": self.balance
        }
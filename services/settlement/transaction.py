import uuid
from datetime import datetime


class Transaction:
    """Represents a financial transaction record."""

    def __init__(self, trade_id: str, buyer_id: str, seller_id: str, amount: float):
        self.transaction_id = str(uuid.uuid4())
        self.trade_id = trade_id
        self.buyer_id = buyer_id
        self.seller_id = seller_id
        self.amount = amount
        self.status = "pending"
        self.created_at = datetime.utcnow().isoformat()

    def to_dict(self):
        return {
            "transaction_id": self.transaction_id,
            "trade_id": self.trade_id,
            "buyer_id": self.buyer_id,
            "seller_id": self.seller_id,
            "amount": self.amount,
            "status": self.status,
            "created_at": self.created_at
        }
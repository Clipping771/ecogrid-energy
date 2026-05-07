import uuid
from services.settlement.wallet import Wallet
from services.settlement.transaction import Transaction


class FinancialSettlementService:
    """
    Financial Settlement Service.
    Processes micro-transactions between buyers and sellers
    in response to TradeConfirmedEvents from the Marketplace.
    """

    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.wallets = {}
        self.transactions = {}
        self.processed_event_ids = set()

        # Subscribe to trade confirmed events from Marketplace
        self.event_bus.subscribe("trade_confirmed", self.handle_trade_confirmed)

    def create_wallet(self, user_id: str, initial_balance: float = 100.0):
        """Create a wallet for a user with an initial balance."""
        wallet = Wallet(user_id, initial_balance)
        self.wallets[user_id] = wallet
        print(f"[Settlement] Wallet created for {user_id} | Balance: ${initial_balance}")
        return wallet

    def handle_trade_confirmed(self, event: dict):
        """
        Handle a TradeConfirmedEvent from the Marketplace.
        Debit the buyer and credit the seller.
        """
        event_id = event["event_id"]

        # Idempotency check — skip if already processed
        if event_id in self.processed_event_ids:
            print(f"[Settlement] Duplicate event {event_id} skipped.")
            return

        self.processed_event_ids.add(event_id)

        trade_id = event["trade_id"]
        buyer_id = event["buyer_id"]
        seller_id = event["seller_id"]
        amount = event["amount_due"]

        transaction = Transaction(trade_id, buyer_id, seller_id, amount)
        self.transactions[transaction.transaction_id] = transaction

        try:
            # Ensure wallets exist
            if buyer_id not in self.wallets:
                raise ValueError(f"Wallet not found for buyer: {buyer_id}")
            if seller_id not in self.wallets:
                raise ValueError(f"Wallet not found for seller: {seller_id}")

            buyer_wallet = self.wallets[buyer_id]
            seller_wallet = self.wallets[seller_id]

            # Process the transaction
            buyer_wallet.debit(amount)
            seller_wallet.credit(amount)
            transaction.status = "completed"

            print(f"[Settlement] Transaction complete: {transaction.transaction_id} | "
                  f"${amount} transferred from {buyer_id} to {seller_id}")
            print(f"[Settlement] Buyer balance: ${buyer_wallet.balance} | "
                  f"Seller balance: ${seller_wallet.balance}")

            # Publish success event
            self.event_bus.publish("settlement_complete", {
                "event_id": str(uuid.uuid4()),
                "event_type": "SettlementCompleteEvent",
                "trade_id": trade_id,
                "transaction_id": transaction.transaction_id
            })

        except ValueError as e:
            transaction.status = "failed"
            print(f"[Settlement] Transaction FAILED for trade {trade_id}: {e}")

            # Publish failure event — triggers compensating transaction in Marketplace
            self.event_bus.publish("settlement_failed", {
                "event_id": str(uuid.uuid4()),
                "event_type": "SettlementFailedEvent",
                "trade_id": trade_id,
                "reason": str(e)
            })
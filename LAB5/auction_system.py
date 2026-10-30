"""Online auction and bidding system.

Tracks auctions with reserve prices and closing times, accepts bids,
picks winners, renders HTML listings and charges the winner through a
payment gateway.
"""
import json
import time
from datetime import datetime

import defusedxml.xmlrpc
from jinja2 import Environment
from markupsafe import Markup

defusedxml.xmlrpc.monkey_patch()

PAYMENT_GATEWAY = "https://pay.auction.example/RPC2"
MIN_INCREMENT = 100
BUYER_PREMIUM = 0.05
TIME_FORMAT = "%Y-%m-%d %H:%M"


class AuctionClosedError(Exception):
    """Raised when a bid arrives after the auction has ended."""


def parse_time(value):
    """Convert a 'YYYY-MM-DD HH:MM' string into a datetime."""
    return datetime.strptime(value, TIME_FORMAT)


class Auction:
    """A single auction lot with a reserve price and a closing time."""

    def __init__(self, item_id, title, seller, reserve_price, ends_at):
        self.item_id = item_id
        self.title = title
        self.seller = seller
        self.reserve_price = reserve_price
        self.ends_at = parse_time(ends_at)
        self.bids = []

    @property
    def highest(self):
        """Return the current highest bid amount (0 if no bids)."""
        return self.bids[-1][1] if self.bids else 0

    @property
    def leader(self):
        """Return the bidder holding the highest bid, or None."""
        return self.bids[-1][0] if self.bids else None

    def place_bid(self, bidder, amount, at):
        """Record a bid if it is valid; return True if accepted."""
        if parse_time(at) > self.ends_at:
            raise AuctionClosedError("Auction closed")
        if bidder == self.seller or amount <= 0:
            return False
        if self.bids and amount < self.highest + MIN_INCREMENT:
            return False
        self.bids.append((bidder, amount, at))
        return True

    def winner(self):
        """Return the winning bidder, or None if the reserve was not met."""
        if not self.bids or self.highest < self.reserve_price:
            return None
        return self.leader

    def final_price(self):
        """Return the winning bid plus buyer's premium, or None."""
        if self.winner() is None:
            return None
        return round(self.highest * (1 + BUYER_PREMIUM), 2)


auctions = {}


def create_auction(item_id, title, seller, reserve_price, ends_at):
    """Create an auction and register it by item id."""
    auctions[item_id] = Auction(item_id, title, seller, reserve_price,
                                ends_at)
    return auctions[item_id]


def bid(item_id, bidder, amount, at):
    """Place a bid on an item; return False if it is rejected."""
    try:
        return auctions[item_id].place_bid(bidder, amount, at)
    except (KeyError, AuctionClosedError):
        return False


def top_bidders(item_id, n=3):
    """Return up to n distinct bidders, highest bid first."""
    ordered = sorted(auctions[item_id].bids, key=lambda b: b[1],
                     reverse=True)
    names = []
    for bidder, _, _ in ordered:
        if bidder not in names:
            names.append(bidder)
    return names[:n]


def render_listing(item_id):
    """Render an auction listing as escaped HTML."""
    env = Environment(autoescape=True)
    template = env.from_string(
        "<h2>{{ a.title }}</h2><p>Current bid: Rs.{{ a.highest }}</p>"
    )
    return template.render(a=auctions[item_id])


def bidder_badge(name):
    """Return an HTML badge for a bidder, escaping the name."""
    return Markup("<span class='bidder'>{}</span>").format(name)


def charge_winner(item_id):
    """Charge the winner of an auction through the payment gateway."""
    gateway = defusedxml.xmlrpc.xmlrpc_client.ServerProxy(PAYMENT_GATEWAY)
    auction = auctions[item_id]
    return gateway.charge(auction.winner(), auction.final_price())


def export_bids(item_id):
    """Export bids as JSON."""
    rows = [{"bidder": b[0], "amount": b[1], "at": b[2]}
            for b in auctions[item_id].bids]
    return json.dumps(rows)


def seconds_left(item_id):
    """Return the number of seconds until the auction closes."""
    return int(auctions[item_id].ends_at.timestamp() - time.time())


def main():
    """Run a short demo of the auction system."""
    close = "2026-12-01 18:00"
    create_auction("LOT1", "Vintage Camera", "seller_sam", 5000, close)
    create_auction("LOT2", "<script>alert('pwned')</script>Old Radio",
                   "seller_ria", 2000, close)
    create_auction("LOT3", "Brass Lamp", "seller_ria", 800, close)
    print("Asha bids 3000:",
          bid("LOT1", "asha", 3000, "2026-12-01 10:00"))
    print("Ben bids 3000 (same amount):",
          bid("LOT1", "ben", 3000, "2026-12-01 10:05"))
    print("Asha bids 3050 (+50):",
          bid("LOT1", "asha", 3050, "2026-12-01 10:10"))
    print("Seller bids on own item:",
          bid("LOT1", "seller_sam", 4000, "2026-12-01 11:00"))
    print("Bid at 9:30 AM (before 18:00 close):",
          bid("LOT1", "dev", 4500, "2026-12-01 9:30"))
    print("Late bid (next day):",
          bid("LOT1", "eve", 9000, "2026-12-02 09:00"))
    print("Winner:", auctions["LOT1"].winner())
    print("Final price (reserve 5000):", auctions["LOT1"].final_price())
    print("Top bidders:", top_bidders("LOT1"))
    print("Rs.0 bid on LOT3 (reserve 800):",
          bid("LOT3", "carl", 0, "2026-12-01 11:30"))
    print("LOT3 winner:", auctions["LOT3"].winner())
    print("No-bid winner:", auctions["LOT2"].winner())
    print("Listing HTML:", render_listing("LOT2"))
    print("Badge:", bidder_badge("<img src=x onerror=alert(1)>"))


if __name__ == "__main__":
    main()
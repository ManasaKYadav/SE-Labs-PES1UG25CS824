# Lab 5 – Issues Found

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Insecure XML-RPC import (B411) | Security – High | 5, 73 | `xmlrpc.client` is vulnerable to XML attacks when parsing untrusted responses | Use `defusedxml.xmlrpc`, call `monkey_patch()` |
| Jinja2 autoescape disabled (B701) | Security – High | 65 | `<script>` in an auction title is rendered unescaped (XSS) | `Environment(autoescape=True)` |
| Unsafe Markup (B704) | Security – Medium | 70 | User name concatenated into `Markup`, so HTML is trusted (XSS) | `Markup("...{}...").format(name)` escapes input |
| String time comparison | Bug | 22 | `"9:30" > "18:00"` as strings, so a valid bid is rejected | Parse times with `datetime.strptime` |
| Equal / small bids accepted | Bug | 24 | `>=` accepts equal bids; `MIN_INCREMENT` never used | Require `amount >= highest + MIN_INCREMENT` |
| Seller bids on own item | Bug | 21–30 | Allows shill bidding | Reject bids where `bidder == seller` |
| Reserve price ignored | Bug | 32–38 | Winner and price returned even below reserve | Return `None` if `highest < reserve_price` |
| Rs.0 bid accepted | Bug | 24 | `highest` starts at 0, so a 0 bid wins | Reject `amount <= 0` |
| Broad exception raised/caught | Pylint W0719/W0718 | 23, 50 | Generic `Exception` hides real errors | Custom `AuctionClosedError`; catch specific exceptions |
| Attribute outside `__init__` | Pylint W0201 | 27 | `leader` undefined until first bid | Made `highest`/`leader` properties |
| Naming / docstrings / imports | Pylint C0103/C0114/C0116/C0411 | many | camelCase names, no docstrings, wrong import order | snake_case, docstrings, stdlib imports first |
| Blank lines / long lines | Flake8 E302/E305/E501 | many | PEP 8 spacing and >79-char lines | 2 blank lines between defs, wrap long lines |

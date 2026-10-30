\# Lab 5 – Reflection



\## 1. Which issues were the easiest to fix, and which were the hardest? Why?



The easiest issues were the Flake8 style warnings (E302/E305 blank lines and E501

long lines) and Bandit's B701. They were purely mechanical: adding blank lines,

wrapping long lines, and changing `autoescape=False` to `autoescape=True` in one

place. Pylint's naming (camelCase to snake\_case) and missing-docstring warnings

were also simple, though I had to update every call to the renamed functions.



The hardest was B411 (insecure `xmlrpc.client`). Adding

`defusedxml.xmlrpc.monkey\_patch()` alone did not clear the warning, because Bandit

flags the import itself, so I had to switch to using `defusedxml.xmlrpc` for the

import and the ServerProxy. The logic bugs were even harder, because no tool

reported them. I found them only by reading the program's output: bids times

compared as strings (so a valid 9:30 bid was rejected), the reserve price being

ignored, equal and +50 bids accepted even though MIN\_INCREMENT was defined, a

seller bidding on their own item, and a Rs.0 bid being accepted.



\## 2. Did the static analysis tools report any false positives? If so, describe one example.



Yes, partly. Bandit's B411 is arguably a false positive in this program: the

payment gateway URL is a fixed, trusted server, but Bandit flags any use of

`xmlrpc.client` regardless of context. I still fixed it, because using defusedxml

costs little and protects against a compromised or spoofed server.



Some Pylint messages were style preferences rather than real defects, for example

R0902 (too many instance attributes, 8/7) and the missing-docstring warnings. The

code worked correctly despite them. On the other hand, the tools also had false

negatives: none of them detected the logic bugs, which were the most serious

problems in the program.



\## 3. How would you integrate static analysis tools into your actual software development workflow?



\- Local development: run Flake8 and Pylint inside the editor (VS Code extensions)

&#x20; so issues appear while typing, and use a pre-commit hook that runs Flake8,

&#x20; Pylint and Bandit before each commit.

\- Continuous Integration: add a GitHub Actions workflow that runs all three tools

&#x20; on every push and pull request, and fails the build if Bandit reports any

&#x20; High-severity issue, Flake8 reports any error, or the Pylint score drops below

&#x20; 9.5.

\- Configuration: keep shared settings (line length, disabled checks) in a config

&#x20; file such as `setup.cfg` or `.pylintrc` so the whole team uses the same rules.

\- Since the tools cannot catch logic errors, combine them with unit tests and

&#x20; code review.



\## 4. What tangible improvements did you observe in the code quality, readability, or potential robustness after applying the fixes?



\- Scores: the Pylint score went from 6.09/10 to 10.00/10, Bandit went from

&#x20; 3 issues (2 High, 1 Medium) to none, and Flake8 went from 19 warnings to 0.

\- Security: auction titles and bidder names are now HTML-escaped, so the

&#x20; `<script>` and `<img onerror>` XSS payloads are no longer executed, and

&#x20; XML-RPC responses are parsed safely with defusedxml.

\- Robustness: a custom `AuctionClosedError` replaced the generic

&#x20; `raise Exception` / `except Exception`, so unrelated errors are no longer

&#x20; silently hidden. `highest` and `leader` are now properties, so `leader` can

&#x20; never be undefined.

\- Correctness: bids must beat the current highest by MIN\_INCREMENT, sellers

&#x20; cannot bid on their own items, zero bids are rejected, times are compared as

&#x20; real datetimes, and no winner or final price is returned when the reserve is

&#x20; not met.

\- Readability: snake\_case names, docstrings on every function, grouped imports,

&#x20; and a `if \_\_name\_\_ == "\_\_main\_\_":` guard make the code easier to read and

&#x20; safe to import.


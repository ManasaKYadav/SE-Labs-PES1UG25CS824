# Number Guessing Repair Lab

An interactive number deduction game built with **Pygame**. This project covers string-to-integer parsing safety, input sanitization, dynamic range feedback, game state management, and text-input UI widgets in an object-oriented codebase.

All four lab tasks (one bug fix and three features) have been completed using an LLM (Claude) as a debugging and pair-programming partner.

**LLM chat :** https://claude.ai/share/c101db18-0944-40b7-8206-49b1c9e7d518

---

## Features

- A secret number between 1 and 100, generated on start and on every restart
- A custom `TextBox` widget that accepts digits and backspace, with an active/inactive state
- Guess submission via `Return` / `Enter` or the `SUBMIT` button
- Hint feedback: `TOO LOW!`, `TOO HIGH!`, or `CORRECT!`
- **Safe handling of empty submissions** (Task 1)
- **Dynamic "Current Possible Range: X - Y" display** (Task 2)
- **Recent guess history panel with colored direction indicators** (Task 3)
- **Maximum of 7 attempts with a Game Over screen** (Task 4)

---

## Getting Started

### Setup

1. Make sure you have Python 3.10+ installed.
2. Install dependencies:

```bash
pip install pygame
```

3. Run the game:

```bash
python main.py
```

### Controls

| Action | Input |
|---|---|
| Type a guess | Number keys (up to 4 digits) |
| Delete a digit | Backspace |
| Submit a guess | Return / Enter, or click SUBMIT |
| Start a new game | `R` (after winning or losing) |

---

## Tasks Completed

### Task 1: Fix the empty input crash bug

**Cause:** `TextBox.text` starts as `""` and is cleared back to `""` after every guess. Submitting with nothing typed called `int("")` inside `submit_guess()`, and Python raises `ValueError: invalid literal for int() with base 10: ''` because an empty string is not a valid integer.

**Fix:** In `game_engine.py`, `submit_guess()` now checks for empty text before any conversion happens:

```python
if not self.input_box.text:
    self.feedback_msg = "Please enter a valid number first!"
    self.feedback_color = (240, 190, 60)
    return

guess = int(self.input_box.text)
```

The early `return` happens before `int()` is called and before `self.attempts += 1`, so an empty submission shows an amber warning, does not crash, and does not use up an attempt.

### Task 2: Dynamic search range display

**Implementation:** The engine tracks `low_bound` (starts at 1) and `high_bound` (starts at 100).

- A "too low" guess raises the lower bound: `low_bound = max(low_bound, guess + 1)`
- A "too high" guess lowers the upper bound: `high_bound = min(high_bound, guess - 1)`
- Using `max` / `min` means a guess already outside the known range can never loosen the bounds.
- On a correct guess, both bounds collapse to the answer.
- Both bounds are reset in `reset()`.

The range is rendered on screen as **"Current Possible Range: X - Y"**.

### Task 3: Recent guess history tracker

**Implementation:** Every valid guess is stored in `self.history` as a `(guess, result)` tuple, where `result` is `"LOW"`, `"HIGH"`, or `"CORRECT"`. A `render_history()` method draws a panel below the feedback area showing the **last 5 guesses, newest first**, each with its original attempt number (`#1`, `#2`, ...).

Each row has a colored indicator:

| Result | Indicator | Color |
|---|---|---|
| Too low (go higher) | Up arrow + `TOO LOW` | Blue |
| Too high (go lower) | Down arrow + `TOO HIGH` | Red |
| Correct | Dot + `CORRECT` | Green |

The arrows are drawn as polygons instead of text characters, because `pygame.font.SysFont(None, ...)` often cannot render Unicode arrows and shows empty boxes instead. Empty submissions never reach the history because they return early.

### Task 4: Maximum attempts constraint and failure state

**Implementation:** `MAX_ATTEMPTS = 7`. The old `game_won` boolean was replaced by a state variable with three values:

- `PLAYING` - a round is in progress
- `WON` - the player guessed the number
- `GAME_OVER` - the player used all 7 attempts without guessing

Key behaviors:

- `submit_guess()` returns immediately unless the state is `PLAYING`, so no further guesses count after a win or loss.
- A correct guess is checked first, so guessing the number on attempt 7 is a **win**, not a game over.
- After the 7th wrong guess, the feedback line shows **"GAME OVER! The number was N"** and the screen shows **"Press R to try again"**.
- The attempt counter displays `Attempts: X / 7` and turns red on the last attempt.
- The text box ignores typing once the round is over.
- `reset()` fully resets the secret number, attempts, bounds, history, feedback message, state, and input box. `__init__` calls `reset()` so the starting values are defined in one place only.

---

## Expected Behavior

- Typing numbers and pressing Return or clicking SUBMIT registers a guess.
- Submitting an empty input box shows a warning message without crashing and without counting an attempt.
- Each valid guess reports too high or too low and increments the attempt count.
- The possible range narrows after each valid guess.
- The history panel lists the last 5 guesses with colored direction indicators.
- Guessing the exact number shows the victory message and unlocks `R` to restart.
- Using all 7 attempts without a correct guess shows the Game Over screen with the secret number, and `R` fully resets the game.

---

## Folder Structure

```
number_guess/
├── game/
│   ├── game_engine.py
│   └── text_box.py
├── main.py
└── README.md
```

### Files changed from the original

| File | Change |
|---|---|
| `game/game_engine.py` | Empty-input fix, range tracking, history panel, attempt limit, state handling |
| `main.py` | Window height raised from 380 to 500 so the history panel fits |
| `game/text_box.py` | Unchanged |

---

## Submission Checklist

- [ ] A 10-second video of gameplay **before** the changes, showing the bug
- [ ] A 10-second video of gameplay **after** the changes, showing the bug fixed and the new features working
- [x] The Chat/LLM used page link, with the complete chat history: https://claude.ai/share/c101db18-0944-40b7-8206-49b1c9e7d518

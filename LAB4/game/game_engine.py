import random
import pygame
from game.text_box import TextBox

MAX_ATTEMPTS = 7

# Game states
PLAYING = "PLAYING"
WON = "WON"
GAME_OVER = "GAME_OVER"

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.input_box = TextBox(width // 2 - 110, 150, 120, 48)
        self.submit_btn = pygame.Rect(width // 2 + 25, 150, 100, 48)

        self.font_title = pygame.font.SysFont(None, 42)
        self.font_medium = pygame.font.SysFont(None, 28)
        self.font_small = pygame.font.SysFont(None, 24)
        self.font_btn = pygame.font.SysFont(None, 26)

        self.reset()

    def reset(self):
        self.secret_number = random.randint(1, 100)
        self.attempts = 0
        self.low_bound = 1
        self.high_bound = 100
        self.history = []  # list of (guess, result) where result is "LOW", "HIGH" or "CORRECT"
        self.feedback_msg = "Enter a number between 1 and 100"
        self.feedback_color = (220, 220, 220)
        self.state = PLAYING
        self.input_box.clear()
        self.input_box.active = True

    def submit_guess(self):
        if self.state != PLAYING:
            return

        if not self.input_box.text:
            self.feedback_msg = "Please enter a valid number first!"
            self.feedback_color = (240, 190, 60)
            return

        guess = int(self.input_box.text)

        self.attempts += 1
        self.input_box.clear()

        if guess == self.secret_number:
            self.feedback_msg = f"CORRECT! Found in {self.attempts} attempts."
            self.feedback_color = (80, 220, 90)
            self.low_bound = self.high_bound = guess
            self.history.append((guess, "CORRECT"))
            self.state = WON
            return

        if guess < self.secret_number:
            self.feedback_msg = f"TOO LOW! (Guess was {guess})"
            self.feedback_color = (80, 160, 240)
            self.low_bound = max(self.low_bound, guess + 1)
            self.history.append((guess, "LOW"))
        else:
            self.feedback_msg = f"TOO HIGH! (Guess was {guess})"
            self.feedback_color = (240, 100, 80)
            self.high_bound = min(self.high_bound, guess - 1)
            self.history.append((guess, "HIGH"))

        # Out of attempts without a correct guess
        if self.attempts >= MAX_ATTEMPTS:
            self.feedback_msg = f"GAME OVER! The number was {self.secret_number}"
            self.feedback_color = (240, 100, 80)
            self.state = GAME_OVER

    def handle_event(self, event):
        # Only accept typing/clicks in the text box while a round is in progress
        if self.state == PLAYING:
            self.input_box.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.submit_guess()
            elif event.key == pygame.K_r and self.state != PLAYING:
                self.reset()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.submit_btn.collidepoint(event.pos):
                self.submit_guess()

    def update(self):
        pass

    def render_history(self, screen):
        panel = pygame.Rect(self.width // 2 - 200, 310, 400, 170)
        pygame.draw.rect(screen, (40, 45, 55), panel, border_radius=8)
        pygame.draw.rect(screen, (90, 95, 105), panel, width=2, border_radius=8)

        header = self.font_medium.render("Last 5 Guesses", True, (245, 245, 245))
        screen.blit(header, (panel.x + 15, panel.y + 10))

        if not self.history:
            empty = self.font_small.render("No guesses yet", True, (130, 135, 145))
            screen.blit(empty, (panel.x + 15, panel.y + 42))
            return

        recent = self.history[-5:][::-1]  # newest first
        for i, (guess, result) in enumerate(recent):
            number = len(self.history) - i
            y = panel.y + 40 + i * 25
            cx, cy = panel.x + 175, y + 9

            num_surf = self.font_small.render(f"#{number}", True, (130, 135, 145))
            screen.blit(num_surf, (panel.x + 15, y))

            guess_surf = self.font_small.render(str(guess), True, (245, 245, 245))
            screen.blit(guess_surf, (panel.x + 70, y))

            if result == "LOW":
                color, tag = (80, 160, 240), "TOO LOW"
                points = [(cx, cy - 7), (cx - 7, cy + 6), (cx + 7, cy + 6)]  # up: go higher
                pygame.draw.polygon(screen, color, points)
            elif result == "HIGH":
                color, tag = (240, 100, 80), "TOO HIGH"
                points = [(cx - 7, cy - 6), (cx + 7, cy - 6), (cx, cy + 7)]  # down: go lower
                pygame.draw.polygon(screen, color, points)
            else:
                color, tag = (80, 220, 90), "CORRECT"
                pygame.draw.circle(screen, color, (cx, cy), 7)

            tag_surf = self.font_small.render(tag, True, color)
            screen.blit(tag_surf, (cx + 20, y))

    def render(self, screen):
        screen.fill((30, 34, 42))

        title_surf = self.font_title.render("Number Guessing Arena", True, (245, 245, 245))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 35))

        attempts_color = (240, 100, 80) if self.attempts >= MAX_ATTEMPTS - 1 else (180, 185, 195)
        attempts_surf = self.font_medium.render(
            f"Attempts: {self.attempts} / {MAX_ATTEMPTS}", True, attempts_color
        )
        screen.blit(attempts_surf, (self.width // 2 - attempts_surf.get_width() // 2, 95))
        self.input_box.render(screen)

        pygame.draw.rect(screen, (50, 150, 80), self.submit_btn, border_radius=6)
        pygame.draw.rect(screen, (220, 220, 220), self.submit_btn, width=2, border_radius=6)
        btn_text = self.font_btn.render("SUBMIT", True, (255, 255, 255))
        screen.blit(
            btn_text,
            (self.submit_btn.centerx - btn_text.get_width() // 2, self.submit_btn.centery - btn_text.get_height() // 2),
        )

        range_surf = self.font_medium.render(
            f"Current Possible Range: {self.low_bound} - {self.high_bound}", True, (150, 200, 255)
        )
        screen.blit(range_surf, (self.width // 2 - range_surf.get_width() // 2, 210))

        feedback_surf = self.font_medium.render(self.feedback_msg, True, self.feedback_color)
        screen.blit(feedback_surf, (self.width // 2 - feedback_surf.get_width() // 2, 245))

        if self.state == WON:
            restart_surf = self.font_medium.render("Press [R] to Start a New Game", True, (255, 220, 80))
            screen.blit(restart_surf, (self.width // 2 - restart_surf.get_width() // 2, 275))
        elif self.state == GAME_OVER:
            restart_surf = self.font_medium.render("Press R to try again", True, (255, 220, 80))
            screen.blit(restart_surf, (self.width // 2 - restart_surf.get_width() // 2, 275))

        self.render_history(screen)
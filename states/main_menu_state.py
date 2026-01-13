import sys
from typing import TYPE_CHECKING

import pygame

from constants import FONT_SIZE_LARGE, FONT_SIZE_MEDIUM, SCREEN_HEIGHT, SCREEN_WIDTH
from .base_state import BaseState, GameStateType

if TYPE_CHECKING:
    from game import Game


class MainMenuState(BaseState):
    """Main menu with New Game, High Scores, Quit options."""

    MENU_OPTIONS = ["New Game", "High Scores", "Quit"]

    def __init__(self, game: "Game"):
        super().__init__(game)
        self.selected_index = 0
        self.high_score = 0
        self.title_font = None
        self.menu_font = None
        self.score_font = None

    def enter(self):
        self.selected_index = 0
        self.high_score = self.game.score_repository.get_highest_score()
        pygame.font.init()
        self.title_font = pygame.font.Font(None, FONT_SIZE_LARGE)
        self.menu_font = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        self.score_font = pygame.font.Font(None, FONT_SIZE_MEDIUM)

    def exit(self):
        pass

    def handle_event(self, event: pygame.event.Event) -> GameStateType | None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.MENU_OPTIONS)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.MENU_OPTIONS)
            elif event.key == pygame.K_RETURN:
                return self._select_option()
        return None

    def _select_option(self) -> GameStateType | None:
        option = self.MENU_OPTIONS[self.selected_index]
        if option == "New Game":
            return GameStateType.PLAYING
        elif option == "High Scores":
            return GameStateType.HIGH_SCORES
        elif option == "Quit":
            pygame.quit()
            sys.exit()
        return None

    def update(self, dt: float) -> GameStateType | None:
        return None

    def render(self, screen: pygame.Surface):
        screen.fill("black")

        # Render title "ASTEROIDS"
        title_text = self.title_font.render("ASTEROIDS", True, "white")
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title_text, title_rect)

        # Render menu options
        start_y = SCREEN_HEIGHT // 2 - 50
        for i, option in enumerate(self.MENU_OPTIONS):
            color = "yellow" if i == self.selected_index else "white"
            prefix = "> " if i == self.selected_index else "  "
            text = self.menu_font.render(f"{prefix}{option}", True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * 60))
            screen.blit(text, text_rect)

        # Render high score at bottom
        if self.high_score > 0:
            score_text = self.score_font.render(
                f"HIGH SCORE: {self.high_score}", True, "cyan"
            )
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
            screen.blit(score_text, score_rect)

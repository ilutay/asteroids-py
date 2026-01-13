from typing import TYPE_CHECKING

import pygame

from constants import FONT_SIZE_LARGE, FONT_SIZE_MEDIUM, FONT_SIZE_SMALL, SCREEN_HEIGHT, SCREEN_WIDTH
from .base_state import BaseState, GameStateType

if TYPE_CHECKING:
    from game import Game


class GameOverState(BaseState):
    """Game over screen with high score entry."""

    MENU_OPTIONS = ["Play Again", "Main Menu"]
    MAX_NAME_LENGTH = 20

    def __init__(self, game: "Game"):
        super().__init__(game)
        self.is_high_score = False
        self.player_name = ""
        self.name_submitted = False
        self.selected_index = 0
        self.title_font = None
        self.menu_font = None
        self.info_font = None

    def enter(self):
        self.is_high_score = self.game.score_repository.is_high_score(self.game.final_score)
        self.player_name = ""
        self.name_submitted = False
        self.selected_index = 0
        pygame.font.init()
        self.title_font = pygame.font.Font(None, FONT_SIZE_LARGE)
        self.menu_font = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        self.info_font = pygame.font.Font(None, FONT_SIZE_SMALL)

    def exit(self):
        pass

    def handle_event(self, event: pygame.event.Event) -> GameStateType | None:
        if self.is_high_score and not self.name_submitted:
            return self._handle_name_input(event)
        else:
            return self._handle_menu_input(event)

    def _handle_name_input(self, event: pygame.event.Event) -> GameStateType | None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and len(self.player_name) > 0:
                self.game.score_repository.save_score(self.player_name, self.game.final_score)
                self.name_submitted = True
            elif event.key == pygame.K_BACKSPACE:
                self.player_name = self.player_name[:-1]
            elif len(self.player_name) < self.MAX_NAME_LENGTH:
                if event.unicode.isprintable() and event.unicode and event.unicode != " " or (event.unicode == " " and len(self.player_name) > 0):
                    self.player_name += event.unicode
        return None

    def _handle_menu_input(self, event: pygame.event.Event) -> GameStateType | None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.MENU_OPTIONS)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.MENU_OPTIONS)
            elif event.key == pygame.K_RETURN:
                option = self.MENU_OPTIONS[self.selected_index]
                if option == "Play Again":
                    return GameStateType.PLAYING
                elif option == "Main Menu":
                    return GameStateType.MAIN_MENU
        return None

    def update(self, dt: float) -> GameStateType | None:
        return None

    def render(self, screen: pygame.Surface):
        screen.fill("black")

        # Render "GAME OVER"
        title_text = self.title_font.render("GAME OVER", True, "red")
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 120))
        screen.blit(title_text, title_rect)

        # Render final score
        score_text = self.menu_font.render(
            f"Final Score: {self.game.final_score}", True, "white"
        )
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        screen.blit(score_text, score_rect)

        if self.is_high_score and not self.name_submitted:
            # Render high score entry
            congrats_text = self.menu_font.render("NEW HIGH SCORE!", True, "yellow")
            congrats_rect = congrats_text.get_rect(center=(SCREEN_WIDTH // 2, 280))
            screen.blit(congrats_text, congrats_rect)

            prompt_text = self.info_font.render("Enter your name:", True, "white")
            prompt_rect = prompt_text.get_rect(center=(SCREEN_WIDTH // 2, 340))
            screen.blit(prompt_text, prompt_rect)

            # Render name input box
            name_display = self.player_name + "_"
            name_text = self.menu_font.render(name_display, True, "cyan")
            name_rect = name_text.get_rect(center=(SCREEN_WIDTH // 2, 400))
            screen.blit(name_text, name_rect)

            hint_text = self.info_font.render("Press ENTER to confirm", True, "gray")
            hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, 460))
            screen.blit(hint_text, hint_rect)
        else:
            # Render menu options
            start_y = SCREEN_HEIGHT // 2 + 50
            for i, option in enumerate(self.MENU_OPTIONS):
                color = "yellow" if i == self.selected_index else "white"
                prefix = "> " if i == self.selected_index else "  "
                text = self.menu_font.render(f"{prefix}{option}", True, color)
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * 60))
                screen.blit(text, text_rect)

from typing import TYPE_CHECKING

import pygame

from constants import (
    FONT_SIZE_LARGE,
    FONT_SIZE_MEDIUM,
    FONT_SIZE_SMALL,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
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
        self.submitting = False
        self.should_submit = False
        self.loading = True
        self.selected_index = 0
        self.title_font = None
        self.menu_font = None
        self.info_font = None

    async def enter(self):
        self.player_name = ""
        self.name_submitted = False
        self.submitting = False
        self.should_submit = False
        self.loading = True
        self.selected_index = 0
        self.is_high_score = False
        pygame.font.init()
        self.title_font = pygame.font.Font(None, FONT_SIZE_LARGE)
        self.menu_font = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        self.info_font = pygame.font.Font(None, FONT_SIZE_SMALL)

    async def exit(self):
        pass

    async def handle_event(self, event: pygame.event.Event) -> GameStateType | None:
        if self.loading or self.submitting:
            return None
        if self.is_high_score and not self.name_submitted:
            return self._handle_name_input(event)
        else:
            return self._handle_menu_input(event)

    def _handle_name_input(self, event: pygame.event.Event) -> GameStateType | None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and len(self.player_name) > 0:
                self.should_submit = True
            elif event.key == pygame.K_BACKSPACE:
                self.player_name = self.player_name[:-1]
            elif len(self.player_name) < self.MAX_NAME_LENGTH:
                char = event.unicode
                is_valid_char = char and char.isprintable()
                is_allowed_space = char == " " and len(self.player_name) > 0
                is_non_space = char != " "
                if is_valid_char and (is_non_space or is_allowed_space):
                    self.player_name += char
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

    async def update(self, dt: float) -> GameStateType | None:
        # Check if this is a high score on first update
        if self.loading:
            self.is_high_score = await self.game.score_repository.is_high_score(
                self.game.final_score
            )
            self.loading = False

        # Handle score submission
        if self.should_submit and not self.submitting:
            self.submitting = True
            await self.game.score_repository.save_score(
                self.player_name, self.game.final_score
            )
            self.submitting = False
            self.should_submit = False
            self.name_submitted = True

        return None

    async def render(self, screen: pygame.Surface):
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

        if self.loading:
            loading_text = self.info_font.render("Loading...", True, "gray")
            loading_rect = loading_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            )
            screen.blit(loading_text, loading_rect)
        elif self.is_high_score and not self.name_submitted:
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

            if self.submitting:
                hint_text = self.info_font.render("Saving...", True, "yellow")
            else:
                hint_text = self.info_font.render(
                    "Press ENTER to confirm", True, "gray"
                )
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

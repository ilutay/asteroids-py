from typing import TYPE_CHECKING

import pygame

from constants import FONT_SIZE_LARGE, FONT_SIZE_MEDIUM, SCREEN_HEIGHT, SCREEN_WIDTH
from .base_state import BaseState, GameStateType

if TYPE_CHECKING:
    from game import Game


class PausedState(BaseState):
    """Pause menu overlay."""

    MENU_OPTIONS = ["Resume", "Main Menu"]

    def __init__(self, game: "Game"):
        super().__init__(game)
        self.selected_index = 0
        self.title_font = None
        self.menu_font = None

    async def enter(self):
        self.selected_index = 0
        pygame.font.init()
        self.title_font = pygame.font.Font(None, FONT_SIZE_LARGE)
        self.menu_font = pygame.font.Font(None, FONT_SIZE_MEDIUM)

    async def exit(self):
        pass

    async def handle_event(self, event: pygame.event.Event) -> GameStateType | None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return GameStateType.PLAYING  # Resume on ESC
            elif event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.MENU_OPTIONS)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.MENU_OPTIONS)
            elif event.key == pygame.K_RETURN:
                return self._select_option()
        return None

    def _select_option(self) -> GameStateType | None:
        option = self.MENU_OPTIONS[self.selected_index]
        if option == "Resume":
            return GameStateType.PLAYING
        elif option == "Main Menu":
            return GameStateType.MAIN_MENU
        return None

    async def update(self, dt: float) -> GameStateType | None:
        return None

    async def render(self, screen: pygame.Surface):
        # First render the frozen game underneath (from playing state)
        playing_state = self.game.states[GameStateType.PLAYING]
        await playing_state.render(screen)

        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # Render "PAUSED" text
        paused_text = self.title_font.render("PAUSED", True, "white")
        paused_rect = paused_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80)
        )
        screen.blit(paused_text, paused_rect)

        # Render menu options
        start_y = SCREEN_HEIGHT // 2
        for i, option in enumerate(self.MENU_OPTIONS):
            color = "yellow" if i == self.selected_index else "white"
            prefix = "> " if i == self.selected_index else "  "
            text = self.menu_font.render(f"{prefix}{option}", True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * 50))
            screen.blit(text, text_rect)

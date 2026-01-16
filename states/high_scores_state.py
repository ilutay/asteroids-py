from typing import TYPE_CHECKING, Any

import pygame

from constants import (
    FONT_SIZE_LARGE,
    FONT_SIZE_SMALL,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from database.storage import RemoteAPIStorage
from utils.platform import is_web

from .base_state import BaseState, GameStateType

if TYPE_CHECKING:
    from game import Game


class HighScoresState(BaseState):
    """Display top 10 high scores."""

    def __init__(self, game: "Game") -> None:
        super().__init__(game)
        self.scores: list[Any] = []
        self.loading = False
        self.title_font: pygame.font.Font | None = None
        self.score_font: pygame.font.Font | None = None
        self.hint_font: pygame.font.Font | None = None

    def enter(self) -> None:
        pygame.font.init()
        self.title_font = pygame.font.Font(None, FONT_SIZE_LARGE)
        self.score_font = pygame.font.Font(None, FONT_SIZE_SMALL)
        self.hint_font = pygame.font.Font(None, FONT_SIZE_SMALL)

        # For web, trigger async loading
        if is_web() and isinstance(self.game.score_repository, RemoteAPIStorage):
            self.loading = True
            self.scores = []
            self.game.score_repository.load_scores_async()
        else:
            self.scores = self.game.score_repository.get_top_scores(10)
            self.loading = False

    def exit(self) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> GameStateType | None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                return GameStateType.MAIN_MENU
        return None

    def update(self, dt: float) -> GameStateType | None:
        # For web, poll for async-loaded scores
        if self.loading and isinstance(self.game.score_repository, RemoteAPIStorage):
            scores = self.game.score_repository.get_top_scores(10)
            if scores:
                self.scores = scores
                self.loading = False
        return None

    def render(self, screen: pygame.Surface) -> None:
        screen.fill("black")

        if self.title_font is None or self.score_font is None or self.hint_font is None:
            return

        # Render title
        title_text = self.title_font.render("HIGH SCORES", True, "yellow")
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
        screen.blit(title_text, title_rect)

        if self.loading:
            loading_text = self.score_font.render("Loading scores...", True, "gray")
            loading_rect = loading_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            )
            screen.blit(loading_text, loading_rect)
        elif not self.scores:
            no_scores_text = self.score_font.render("No scores yet!", True, "gray")
            no_scores_rect = no_scores_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            )
            screen.blit(no_scores_text, no_scores_rect)
        else:
            # Render scores
            start_y = 160
            for i, score in enumerate(self.scores):
                rank = f"{i + 1}."
                name = score.player_name[:15]  # Truncate long names
                points = str(score.score)

                # Render rank
                rank_text = self.score_font.render(rank, True, "cyan")
                screen.blit(rank_text, (SCREEN_WIDTH // 2 - 200, start_y + i * 45))

                # Render name
                name_text = self.score_font.render(name, True, "white")
                screen.blit(name_text, (SCREEN_WIDTH // 2 - 150, start_y + i * 45))

                # Render score (right-aligned)
                points_text = self.score_font.render(points, True, "white")
                points_rect = points_text.get_rect()
                points_rect.right = SCREEN_WIDTH // 2 + 200
                points_rect.top = start_y + i * 45
                screen.blit(points_text, points_rect)

        # Render hint
        hint_text = self.hint_font.render("Press ENTER or ESC to return", True, "gray")
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
        screen.blit(hint_text, hint_rect)

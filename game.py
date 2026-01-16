import asyncio
import sys

import pygame

from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from database import DatabaseConnection, Migrator
from database.repositories import ScoreRepository
from states import (
    BaseState,
    GameOverState,
    GameStateType,
    HighScoresState,
    MainMenuState,
    PausedState,
    PlayingState,
)
from utils.platform import get_storage, is_web


class Game:
    """Main game controller with state machine."""

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Asteroids")
        self.clock = pygame.time.Clock()

        # Initialize storage (local SQLite or remote API based on platform/config)
        if is_web():
            self.db_connection = None
            self.score_repository = get_storage()
        else:
            self.db_connection = DatabaseConnection().get_connection()
            Migrator(self.db_connection).run_migrations()
            repository = ScoreRepository(self.db_connection)
            self.score_repository = get_storage(repository=repository)

        # Shared game data
        self.final_score = 0

        # Initialize states
        self.states: dict[GameStateType, BaseState] = {
            GameStateType.MAIN_MENU: MainMenuState(self),
            GameStateType.PLAYING: PlayingState(self),
            GameStateType.PAUSED: PausedState(self),
            GameStateType.GAME_OVER: GameOverState(self),
            GameStateType.HIGH_SCORES: HighScoresState(self),
        }

        self.current_state_type = GameStateType.MAIN_MENU
        self.current_state.enter()

    @property
    def current_state(self) -> BaseState:
        return self.states[self.current_state_type]

    def change_state(self, new_state_type: GameStateType) -> None:
        """Transition to a new state."""
        old_state_type = self.current_state_type
        self.current_state.exit()
        self.current_state_type = new_state_type

        # Special case: resuming from pause should not reset the game
        if old_state_type == GameStateType.PAUSED and new_state_type == GameStateType.PLAYING:
            # Don't call enter() - just resume
            pass
        else:
            self.current_state.enter()

    async def run(self) -> None:
        """Main game loop (async for pygame-web compatibility)."""
        while True:
            dt = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._quit()

                new_state = self.current_state.handle_event(event)
                if new_state:
                    self.change_state(new_state)

            new_state = self.current_state.update(dt)
            if new_state:
                self.change_state(new_state)

            self.current_state.render(self.screen)
            pygame.display.flip()

            # Yield to browser event loop (required for pygame-web)
            await asyncio.sleep(0)

    def _quit(self) -> None:
        """Clean shutdown."""
        if self.db_connection is not None:
            DatabaseConnection().close()
        pygame.quit()
        sys.exit()

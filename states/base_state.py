from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from game import Game


class GameStateType(Enum):
    MAIN_MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    HIGH_SCORES = auto()


class BaseState(ABC):
    """Abstract base class for all game states."""

    def __init__(self, game: "Game"):
        self.game = game

    @abstractmethod
    def enter(self) -> None:
        """Called when entering this state."""
        pass

    @abstractmethod
    def exit(self) -> None:
        """Called when leaving this state."""
        pass

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> GameStateType | None:
        """Process a single pygame event. Return new state type or None."""
        pass

    @abstractmethod
    def update(self, dt: float) -> GameStateType | None:
        """Update state logic. Return new state type or None."""
        pass

    @abstractmethod
    def render(self, screen: pygame.Surface) -> None:
        """Render this state to the screen."""
        pass

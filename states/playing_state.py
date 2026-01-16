from typing import TYPE_CHECKING, Any

import pygame

from asteroid import Asteroid
from asteroidfield import AsteroidField
from constants import (
    EXTRA_LIFE_POINTS,
    SAFETY_ZONE_RADIUS,
    SCORE_LARGE_ASTEROID,
    SCORE_MEDIUM_ASTEROID,
    SCORE_SMALL_ASTEROID,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    STARTING_LIVES,
)
from player import Player
from shot import Shot
from ui.hud import HUD

from .base_state import BaseState, GameStateType

if TYPE_CHECKING:
    from game import Game


class PlayingState(BaseState):
    """Active gameplay state with game loop logic."""

    def __init__(self, game: "Game") -> None:
        super().__init__(game)
        self.score = 0
        self.lives = STARTING_LIVES
        self.extra_life_threshold = EXTRA_LIFE_POINTS
        self.updatable: pygame.sprite.Group[Any] = pygame.sprite.Group()
        self.drawable: pygame.sprite.Group[Any] = pygame.sprite.Group()
        self.asteroids: pygame.sprite.Group[Any] = pygame.sprite.Group()
        self.shots: pygame.sprite.Group[Any] = pygame.sprite.Group()
        self.player: Player | None = None
        self.asteroid_field: AsteroidField | None = None
        self.hud: HUD | None = None

    def _reset_game_session(self) -> None:
        """Initialize/reset all game session variables."""
        self.score = 0
        self.lives = STARTING_LIVES
        self.extra_life_threshold = EXTRA_LIFE_POINTS

        # Clear sprite groups
        for sprite in list(self.updatable):
            sprite.kill()

        self.updatable = pygame.sprite.Group()
        self.drawable = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.shots = pygame.sprite.Group()

        # Set up containers
        Player.containers = (self.updatable, self.drawable)
        Asteroid.containers = (self.asteroids, self.updatable, self.drawable)
        AsteroidField.containers = (self.updatable,)
        Shot.containers = (self.shots, self.drawable, self.updatable)

        # Create game objects
        self.asteroid_field = AsteroidField()
        self.player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.hud = HUD()

    def enter(self) -> None:
        self._reset_game_session()

    def exit(self) -> None:
        # Kill all sprites
        for sprite in list(self.updatable):
            sprite.kill()

    def handle_event(self, event: pygame.event.Event) -> GameStateType | None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return GameStateType.PAUSED
        return None

    def update(self, dt: float) -> GameStateType | None:
        self.updatable.update(dt)

        if self.player is None:
            return None

        # Check player-asteroid collisions
        for asteroid in list(self.asteroids):
            if not self.player.is_invincible and self.player.collide_with(asteroid):
                result = self._handle_player_death()
                if result:
                    return result

            # Check shot-asteroid collisions
            for shot in list(self.shots):
                if shot.collide_with(asteroid):
                    shot.kill()
                    points = self._get_asteroid_points(asteroid)
                    self.score += points
                    self._check_extra_life()
                    asteroid.split()
                    break  # Asteroid is gone, move to next

        return None

    def _handle_player_death(self) -> GameStateType | None:
        self.lives -= 1
        if self.lives <= 0:
            self.game.final_score = self.score
            return GameStateType.GAME_OVER
        else:
            self._respawn_player()
            return None

    def _respawn_player(self) -> None:
        """Respawn player at center with invincibility."""
        if self.player is None:
            return
        self.player.reset(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.player.start_invincibility()
        self._clear_safety_zone()

    def _clear_safety_zone(self) -> None:
        """Remove asteroids near the spawn point."""
        center = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        for asteroid in list(self.asteroids):
            if center.distance_to(asteroid.position) < SAFETY_ZONE_RADIUS:
                asteroid.kill()

    def _get_asteroid_points(self, asteroid: Asteroid) -> int:
        """Calculate points based on asteroid size (kind)."""
        kind = asteroid.get_kind()
        points_map = {
            3: SCORE_LARGE_ASTEROID,
            2: SCORE_MEDIUM_ASTEROID,
            1: SCORE_SMALL_ASTEROID,
        }
        return points_map.get(kind, 0)

    def _check_extra_life(self) -> None:
        """Award extra life every EXTRA_LIFE_POINTS points."""
        if self.score >= self.extra_life_threshold:
            self.lives += 1
            self.extra_life_threshold += EXTRA_LIFE_POINTS

    def render(self, screen: pygame.Surface) -> None:
        screen.fill("black")
        for obj in self.drawable:
            obj.draw(screen)
        if self.hud is not None:
            self.hud.render(screen, self.score, self.lives)

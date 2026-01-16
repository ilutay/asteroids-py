import random
from typing import override

import pygame

from circleshape import CircleShape
from constants import ASTEROID_MIN_RADIUS, LINE_WIDTH
from logger import log_event


class Asteroid(CircleShape):
    def __init__(self, x: float, y: float, radius: float) -> None:
        super().__init__(x, y, radius)

    def get_kind(self) -> int:
        """Return the kind (1-3) based on radius.

        kind=3: Large (radius=60) -> 20 points
        kind=2: Medium (radius=40) -> 50 points
        kind=1: Small (radius=20) -> 100 points
        """
        return int(round(self.radius / ASTEROID_MIN_RADIUS))

    @override
    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(screen, "white", self.position, self.radius, LINE_WIDTH)

    @override
    def update(self, dt: float) -> None:
        self.position += self.velocity * dt

    def split(self) -> None:
        self.kill()
        if self.radius <= ASTEROID_MIN_RADIUS:
            return
        else:
            log_event("asteroid_split")
            random_angle = random.uniform(20, 50)
            first_asteroid_vector = self.velocity.rotate(random_angle)
            second_asteroid_vector = self.velocity.rotate(-random_angle)
            first_asteroid_radius = self.radius - ASTEROID_MIN_RADIUS
            second_asteroid_radius = self.radius - ASTEROID_MIN_RADIUS
            first_asteroid = Asteroid(
                self.position.x, self.position.y, first_asteroid_radius
            )
            second_asteroid = Asteroid(
                self.position.x, self.position.y, second_asteroid_radius
            )
            first_asteroid.velocity = first_asteroid_vector * 1.2
            second_asteroid.velocity = second_asteroid_vector * 1.2

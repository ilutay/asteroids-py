from typing import override

import pygame
from circleshape import CircleShape
from constants import LINE_WIDTH, SHOT_RADIUS


class Shot(CircleShape):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, SHOT_RADIUS)

    @override
    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(screen, "blue", self.position, self.radius, LINE_WIDTH)

    @override
    def update(self, dt: float) -> None:
        self.position += self.velocity * dt

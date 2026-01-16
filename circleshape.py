from typing import Any, ClassVar

import pygame


# Base class for game objects
class CircleShape(pygame.sprite.Sprite):
    containers: ClassVar[Any]  # Set dynamically by sprite groups

    def __init__(self, x: float, y: float, radius: float) -> None:
        # we will be using this later
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()

        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.radius = radius

    def draw(self, screen: pygame.Surface) -> None:
        # must override
        pass

    def update(self, dt: float) -> None:
        # must override
        pass

    def collide_with(self, other: "CircleShape") -> bool:
        distance = self.position.distance_to(other.position)
        sum_radius = self.radius + other.radius

        if distance > sum_radius:
            return False
        else:
            return True

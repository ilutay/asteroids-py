from typing import override
import pygame
from circleshape import CircleShape
from constants import (
    BLINK_INTERVAL,
    INVINCIBILITY_DURATION,
    LINE_WIDTH,
    PLAYER_RADIUS,
    PLAYER_SHOOT_COOLDOWN_SECONDS,
    PLAYER_SHOOT_SPEED,
    PLAYER_SPEED,
    PLAYER_TURN_SPEED,
)
from shot import Shot


class Player(CircleShape):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, PLAYER_RADIUS)
        self.x = x
        self.y = y
        self.radius = PLAYER_RADIUS
        self.rotation = 0
        self.timer = 0

        # Invincibility system
        self.is_invincible = False
        self.invincibility_timer = 0.0
        self.blink_timer = 0.0
        self.visible = True

    # in the Player class
    def triangle(self) -> list[pygame.Vector2]:
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    @override
    def draw(self, screen: pygame.Surface) -> None:
        # Only draw if visible (for blinking effect during invincibility)
        if self.visible:
            pygame.draw.polygon(screen, "white", self.triangle(), LINE_WIDTH)

    def rotate(self, dt: float) -> None:
        self.rotation += PLAYER_TURN_SPEED * dt

    def start_invincibility(self, duration: float = INVINCIBILITY_DURATION) -> None:
        """Start invincibility period."""
        self.is_invincible = True
        self.invincibility_timer = duration
        self.blink_timer = 0.0
        self.visible = True

    @override
    def update(self, dt: float) -> None:
        self.timer -= dt

        # Update invincibility
        if self.is_invincible:
            self.invincibility_timer -= dt
            self.blink_timer += dt

            # Blink every BLINK_INTERVAL seconds
            if self.blink_timer >= BLINK_INTERVAL:
                self.visible = not self.visible
                self.blink_timer = 0.0

            if self.invincibility_timer <= 0:
                self.is_invincible = False
                self.visible = True

        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            self.rotate(-dt)
        if keys[pygame.K_d]:
            self.rotate(dt)
        if keys[pygame.K_w]:
            self.move(dt)
        if keys[pygame.K_s]:
            self.move(-dt)
        if keys[pygame.K_SPACE]:
            self.shoot()

    def move(self, dt: float) -> None:
        unit_vector = pygame.Vector2(0, 1)
        rotated_vector = unit_vector.rotate(self.rotation)
        rotated_with_speed_vector = rotated_vector * PLAYER_SPEED * dt
        self.position += rotated_with_speed_vector

    def shoot(self) -> None:
        if self.timer > 0:
            return

        self.timer = PLAYER_SHOOT_COOLDOWN_SECONDS
        shot = Shot(self.position.x, self.position.y)
        shot_velocity = pygame.Vector2(0, 1)
        rotated_shot_velocity = shot_velocity.rotate(self.rotation)
        rotated_shot_velocity_with_speed = rotated_shot_velocity * PLAYER_SHOOT_SPEED
        shot.velocity = rotated_shot_velocity_with_speed

    def reset(self, x: float, y: float) -> None:
        """Reset player position and state for respawn."""
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.rotation = 0
        self.timer = 0

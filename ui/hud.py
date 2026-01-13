import pygame

from constants import FONT_SIZE_MEDIUM, FONT_SIZE_SMALL, HUD_MARGIN, SCREEN_WIDTH


class HUD:
    """Heads-up display for score and lives."""

    HEART_SYMBOL = "\u2665"  # Unicode heart

    def __init__(self):
        pygame.font.init()
        self.score_font = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        self.lives_font = pygame.font.Font(None, FONT_SIZE_SMALL)

    def render(self, screen: pygame.Surface, score: int, lives: int):
        """Render score and lives to screen."""
        # Score in top-left
        score_text = self.score_font.render(f"SCORE: {score}", True, "white")
        screen.blit(score_text, (HUD_MARGIN, HUD_MARGIN))

        # Lives in top-right as hearts
        lives_str = self.HEART_SYMBOL * lives
        lives_text = self.lives_font.render(lives_str, True, "red")
        lives_rect = lives_text.get_rect()
        lives_rect.topright = (SCREEN_WIDTH - HUD_MARGIN, HUD_MARGIN)
        screen.blit(lives_text, lives_rect)

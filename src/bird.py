"""Bird entity."""

import pygame

from src.constants import (
    BIRD_LERP,
    BIRD_X,
    COLOR_BIRD_BEAK,
    COLOR_BIRD_BODY,
    COLOR_BIRD_EYE,
    COLOR_BIRD_PUPIL,
    COLOR_BIRD_WING,
    WINDOW_H,
)


class Bird:
    """The player-controlled bird that follows a target pitch Y position."""

    RADIUS_X: int = 18
    RADIUS_Y: int = 13
    EYE_OFFSET: tuple[int, int] = (7, -4)
    EYE_RADIUS: int = 5
    PUPIL_RADIUS: int = 2
    BEAK_LENGTH: int = 8

    def __init__(self) -> None:
        """Initialise the bird at the vertical centre of the screen."""
        self.x: float = float(BIRD_X)
        self.y: float = float(WINDOW_H // 2)
        self.target_y: float = self.y

    def update(self) -> None:
        """Smoothly move the bird toward its target Y using linear interpolation."""
        self.y += (self.target_y - self.y) * BIRD_LERP

    def set_target(self, target_y: float) -> None:
        """Set the Y position the bird should move toward.

        Args:
            target_y (float): Target Y coordinate in pixels.
        """
        self.target_y = target_y

    def draw(self, surface: pygame.Surface) -> None:
        """Render the bird onto a surface.

        Args:
            surface (pygame.Surface): Surface to draw on.
        """
        cx: int = int(self.x)
        cy: int = int(self.y)

        # Wing (slightly offset ellipse below body)
        wing_rect: pygame.Rect = pygame.Rect(cx - 8, cy + 2, 22, 14)
        pygame.draw.ellipse(surface, COLOR_BIRD_WING, wing_rect)

        # Body
        body_rect: pygame.Rect = pygame.Rect(
            cx - self.RADIUS_X, cy - self.RADIUS_Y,
            self.RADIUS_X * 2, self.RADIUS_Y * 2,
        )
        pygame.draw.ellipse(surface, COLOR_BIRD_BODY, body_rect)

        # Eye white
        ex: int = cx + self.EYE_OFFSET[0]
        ey: int = cy + self.EYE_OFFSET[1]
        pygame.draw.circle(surface, COLOR_BIRD_EYE, (ex, ey), self.EYE_RADIUS)

        # Pupil
        pygame.draw.circle(surface, COLOR_BIRD_PUPIL, (ex + 1, ey), self.PUPIL_RADIUS)

        # Beak
        beak_points: list[tuple[int, int]] = [
            (cx + self.RADIUS_X - 2, cy - 2),
            (cx + self.RADIUS_X + self.BEAK_LENGTH, cy + 2),
            (cx + self.RADIUS_X - 2, cy + 5),
        ]
        pygame.draw.polygon(surface, COLOR_BIRD_BEAK, beak_points)

    @property
    def rect(self) -> pygame.Rect:
        """Collision rectangle for the bird.

        Returns:
            pygame.Rect: Bounding rect used for collision detection.
        """
        return pygame.Rect(
            int(self.x) - self.RADIUS_X + 4,
            int(self.y) - self.RADIUS_Y + 4,
            (self.RADIUS_X - 4) * 2,
            (self.RADIUS_Y - 4) * 2,
        )

    def is_out_of_bounds(self) -> bool:
        """Check whether the bird has left the top or bottom of the screen.

        Returns:
            bool: True if the bird is outside the playfield.
        """
        return self.y < 10 or self.y > WINDOW_H - 10

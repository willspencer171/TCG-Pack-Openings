import pygame
from pygame import Surface, Rect
import numpy as np
from src.model.textures import apply_holo_effect


class PygameView:
    def __init__(self, screen_width, screen_height):
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("TCG Pack Openings")
        self.clock = pygame.time.Clock()

    def render_card(self, card_image):
        card_surface = pygame.image.load(card_image)
        card_surface = pygame.transform.scale(card_surface, (400, 533))
        rect = self.center_surface(card_surface)

        self.screen.blit(card_surface, rect)
        return (card_surface, rect)

    def center_surface(self, surface: pygame.Surface):
        rect = surface.get_rect()
        rect.center = self.screen.get_rect().center
        return rect

    def update_holo_anim(
        self,
        effect: callable,
        offset,
        intensity,
        image: Surface,
        rect: Rect,
        array_3d: np.ndarray,
    ):
        holo_effect = apply_holo_effect(effect, offset, intensity, image, array_3d)
        self.screen.blit(holo_effect, rect)

    def render_loading(self, angle=0, spokes=12, radius=40, dot_radius=6, color=(200, 200, 255)):
        center = self.screen.get_rect().center
        for i in range(spokes):
            spoke_angle = angle + (2 * np.pi * i / spokes)
            x = int(center[0] + radius * np.cos(spoke_angle))
            y = int(center[1] + radius * np.sin(spoke_angle))
            # Fade dots for a pinwheel effect
            alpha = (255 * (i+1)) / spokes
            dot_color = (*color, alpha)
            # Create a surface for the dot with per-pixel alpha
            dot_surf = pygame.Surface((dot_radius*2, dot_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(dot_surf, dot_color, (dot_radius, dot_radius), dot_radius)
            self.screen.blit(dot_surf, (x - dot_radius, y - dot_radius))

    def render_inventory(self, inventory):
        font = pygame.font.Font(None, 36)
        text = font.render(
            f"Total Cards: {inventory['total_cards']}", True, (255, 255, 255)
        )
        self.screen.blit(text, (10, 10))

    def render_notification(self, message):
        font = pygame.font.Font(None, 36)
        text = font.render(message, True, (255, 255, 255))
        self.screen.blit(text, (10, 50))

    def update(self):
        pygame.display.flip()
        self.clock.tick(60)

    def clear(self):
        self.screen.fill((0, 0, 0))  # Clear screen with black


class Button:
    def __init__(self, text, width, height, pos):
        self.top_rect = pygame.Rect(pos, (width, height))
        self.top_rect.center = pos
        self.top_colour = "#AAAAAA"

        self.text_surf = pygame.font.Font(None, 28).render(text, True, "#FFFFFF")
        self.text_rect = self.text_surf.get_rect(center=self.top_rect.center)

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, self.top_colour, self.top_rect)
        screen.blit(self.text_surf, self.text_rect)

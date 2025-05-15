import pygame
from src.pack_logic import HashCard, Pack
from src.inventory import Inventory
from src.utils import *

class PygameView:
    def __init__(self, screen_width, screen_height):
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("TCG Pack Openings")
        self.clock = pygame.time.Clock()

    def render_card(self, card_image):
        card_surface = pygame.image.load(card_image)
        self.screen.blit(card_surface, (200, 200))

    def render_inventory(self, inventory):
        font = pygame.font.Font(None, 36)
        text = font.render(f"Total Cards: {inventory['total_cards']}", True, (255, 255, 255))
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

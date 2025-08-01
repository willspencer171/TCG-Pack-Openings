import threading
import asyncio
import aiohttp
from queue import Queue
import numpy as np
import pygame

from src.model.utils import fetch_image
from src.view import PygameView, Button
from src.model.pack_logic import Pack
from src.model.inventory import Inventory
from src.model.textures import holo_shimmer, rainbow_shimmer
from src.model.db import create_tables, populate_data
import config


class Controller:
    def __init__(self):
        self.inventory = Inventory()
        self.image_queue = Queue()
        self.images_loaded = 0
        self.pack_queue = Queue()
        self.pack_loaded = False
        self.pack_opened = False

    def start_image_fetch_thread(self, pack: Pack):
        def run_asyncio():
            asyncio.run(self.async_fetch_images(pack))

        threading.Thread(target=run_asyncio, daemon=True).start()

    def start_pack_gen_thread(self, set_id, ten_pack=False):
        def run_pack_gen():
            self.pack_queue.put(Pack(set_id, ten_pack=ten_pack))

        threading.Thread(target=run_pack_gen, daemon=True).start()

    async def async_fetch_images(self, pack: Pack):
        async with aiohttp.ClientSession() as session:
            for card in pack:
                if hasattr(card, "image_large_url") and card.image_large_url:
                    card_image_data = await fetch_image(session, card.image_large_url)
                    if card_image_data:
                        self.images_loaded += 1
                        self.image_queue.put((card, card_image_data))

            self.pack_loaded = True

    def run(self, set_id, ten_pack=False, rarity_difficulty=2):
        config.RARITY_RANKING, config.RARITY_PROBABILITIES = config.generate_ranking(
            rarity_difficulty
        )
        
        create_tables()
        populate_data()
        self.view = PygameView(800, 800)

        self.start_pack_gen_thread(set_id, ten_pack=ten_pack)
        angle = 0
        while self.pack_queue.empty():
            angle += 0.01
            self.view.render_loading(angle=angle)
            self.view.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            self.view.clear()
        
        pack = self.pack_queue.get()
        self.inventory.add_pack(pack)
        self.inventory.save_inventory()
        self.start_image_fetch_thread(pack)

        while self.images_loaded < len(pack):
            angle += 0.02
            self.view.render_loading(angle=angle)
            self.view.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            self.view.clear()
        self.view.clear()

        self.next_button = Button(
            "Next",
            56,
            28,
            (
                self.view.screen.get_rect().centerx,
                int(self.view.screen.get_rect().height * 0.9),
            ),
        )
        
        holo_offset = 0
        running = True
        current_card = None

        while running:
            if self.pack_loaded:
                self.next_button.draw(self.view.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.pack_loaded and self.next_button.top_rect.collidepoint(pygame.mouse.get_pos()):
                        # Check for new images in the queue
                        if not self.image_queue.empty():
                            self.pack_opened = True
                            card, card_image_data = self.image_queue.get()
                            self.view.clear()
                            current_card = card

                            current_image_surface, current_image_rect = (
                                self.view.render_card(card_image_data)
                            )
                            self.holo_rgb_arr = pygame.surfarray.array3d(
                                current_image_surface
                            ).astype(np.uint8)

                            self.view.update()
                        else:
                            running = False

            if (
                current_card
                and current_card.rarity
                and any(
                    elem in current_card.rarity.lower()
                    for elem in ["rainbow", "shin", "break", "hyper"]
                )
            ):
                holo_offset += 1
                self.view.update_holo_anim(
                    rainbow_shimmer,
                    holo_offset,
                    0.2,
                    current_image_surface,
                    current_image_rect,
                    self.holo_rgb_arr,
                )

            elif current_card and "holo" in current_card.quality:
                holo_offset += 1
                self.view.update_holo_anim(
                    holo_shimmer,
                    holo_offset,
                    0.7,
                    current_image_surface,
                    current_image_rect,
                    self.holo_rgb_arr,
                )

            if self.pack_loaded and not self.pack_opened:
                self.view.render_notification("Pack Loaded!")

            self.view.update()

        pygame.quit()

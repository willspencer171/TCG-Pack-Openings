import threading
import asyncio
import aiohttp
from queue import Queue
from src.utils import fetch_image
from src.view import PygameView
from src.pack_logic import Pack, HashCard
from src.inventory import Inventory
import pygame

class Controller:
    def __init__(self):
        self.inventory = Inventory()
        self.view = PygameView(800, 800)
        self.image_queue = Queue()
        self.pack_loaded = False

    def start_asyncio_thread(self, pack: Pack):
        def run_asyncio():
            asyncio.run(self.async_fetch_images(pack))
        threading.Thread(target=run_asyncio, daemon=True).start()

    async def async_fetch_images(self, pack: Pack):
        async with aiohttp.ClientSession() as session:
            for card in pack:
                if hasattr(card, 'images') and card.images.small:
                    card_image_data = await fetch_image(session, card.images.small)
                    if card_image_data:
                        self.image_queue.put(card_image_data)
            
            self.pack_loaded = True

    def run(self, set_id, ten_pack=False):
        pack = Pack(set_id, ten_pack=ten_pack)
        self.start_asyncio_thread(pack)
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Check for new images in the queue
                    if not self.image_queue.empty():
                        card_image_data = self.image_queue.get()
                        self.view.clear()
                        self.view.render_card(card_image_data)
                        self.view.update()
                    else:
                        running = False
            
            if self.pack_loaded:
                self.view.render_notification("Pack Loaded")
                self.view.update()

        pygame.quit()

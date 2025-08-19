import asyncio
from src.model.api_client import APIClient
from src.model.db_manager import DBManager

from tqdm import tqdm

from config import TCGDEX_LANGUAGE, DATABASE_LOCATION
from src.model.utils import debug_message

class DownloadManager():
    def __init__(self, db_path=DATABASE_LOCATION, threads=4):
        self.api_client = APIClient(TCGDEX_LANGUAGE)
        self.db = DBManager(db_path)
        self.concurrency = threads

    async def populate_progress(self):
        card_resumes = await self.api_client.list_cards()
        for card in card_resumes:
            self.db.fill_progress_table(card.id)

    async def populate_sets(self):
        sets = await self.api_client.list_sets()
        for set in sets:
            self.db.fill_sets_table(set)

    async def fetch_card(self, card_id, semaphore: asyncio.Semaphore, pbar: tqdm):
        async with semaphore:
            try:
                debug_message(f"Trying card {card_id}")
                card = await self.api_client.get_card(card_id)
                self.db.insert_card(card)
                self.db.mark_done(card_id)
                pbar.update(1)
                debug_message(f"✅ Downloaded {card_id}")
            
            except Exception as e:
                self.db.mark_error(card_id)
                debug_message(f"❌ Failed {card_id}: {e}")

    async def download_all(self):
        debug_message("Populating Progress")
        await self.populate_progress()
        debug_message("Populated Progress -- Now populating sets")
        await self.populate_sets()
        debug_message("Populated Sets")
        semaphore = asyncio.Semaphore(self.concurrency)

        done = self.db.n_done
        total = self.db.n_total

        with tqdm(total=total, initial=done, desc="Downloading Progress") as pbar:
            while True:
                pending = self.db.get_pending(limit=self.concurrency * 5)
                if not pending:
                    debug_message("All cards downloaded!")
                    break

                tasks = [
                    self.fetch_card(card_id, semaphore, pbar)
                    for (card_id,) in pending
                ]
                await asyncio.gather(*tasks)

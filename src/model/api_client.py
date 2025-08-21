from tcgdexsdk import TCGdex, CardResume
from asyncio import Semaphore, gather

class APIClient():
    def __init__(self, language='en'):
        self.client = TCGdex(language)
    
    async def list_cards(self):
        return await self.client.card.list()
    
    async def list_sets(self, semaphore: Semaphore):
        sets = await self.client.set.list()
        async def fetch_full(setresume):
            async with semaphore:
                return await setresume.get_full_set()
        
        return await gather(*(fetch_full(s) for s in sets))
    
    async def get_card(self, card_id):
        return await self.client.card.get(card_id)
    
    async def get_full_card(self, card_resume: CardResume):
        return await card_resume.get_full_card()

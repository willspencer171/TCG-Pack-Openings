from tcgdexsdk import TCGdex, CardResume

class APIClient():
    def __init__(self, language='en'):
        self.client = TCGdex(language)
    
    async def list_cards(self):
        return await self.client.card.list()
    
    async def list_sets(self):
        sets = await self.client.set.list()
        return [await set.get_full_set() for set in sets]
    
    async def get_card(self, card_id):
        return await self.client.card.get(card_id)
    
    async def get_full_card(self, card_resume: CardResume):
        return await card_resume.get_full_card()

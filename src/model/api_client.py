from config import TCGDEX
from tcgdexsdk import Query
import asyncio

async def fetch_cards():
    card_resumes = await TCGDEX.card.list(Query())

    full_cards = await asyncio.gather(*[
        card_resume.get_full_card()
        for card_resume
        in card_resumes
    ])

    return full_cards

asyncio.run(fetch_cards())
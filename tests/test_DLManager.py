import pytest
from src.model.download_manager import DownloadManager

from tcgdexsdk import SerieResume, SetResume

@pytest.fixture
def fakeset():
    class FakeSet:
        id = 'xy1'
        name = 'X & Y'
        serie = SerieResume('xy', 'XY', None)
        releaseDate = '16/01/2016'

        async def get_full_set(self):
            return FakeSet()

    return FakeSet()

@pytest.fixture
def fakecard():
    class FakeCard:
        id='xy1-1'
        set=SetResume('xy1', '', '', '', None)
        name='Bulbasaur'
        rarity='Common'
        category='Pokémon'
        localId='1'
        illustrator='HYOGONOSUKE'

        variants={
            'normal': True,
            'holo': True,
            'reverseHolo': False,
            '1stEdition': False,
            'wPromo': False
            }
    
    return FakeCard()

@pytest.mark.asyncio
async def test_download_flow(monkeypatch):
    dm = DownloadManager(db_path=":memory:")

    # Mock API list
    async def fake_list_cards():
        class Resume:
            id = "xy-1"
            async def get_full_card(self):
                class Card:
                    id = "xy-1"
                    name = "Bulbasaur"
                    category = "Pokémon"
                    set = fakeset
                    rarity = "Common"
                    releaseDate = "1999-01-01"
                    def dict(self): return {"id": "xy-1"}
                return Card()
        return [Resume()]
    
    async def fake_set():
        return [fakeset]
    
    async def fake_card():
        return fakecard
    
    """ monkeypatch.setattr(dm.api_client.client.set, 'list', fake_set)

    monkeypatch.setattr(dm.api_client, "list_cards", fake_list_cards)
    monkeypatch.setattr(dm.api_client, "get_card", fake_card) """

    await dm.download_all()

    assert dm.db.count_done() == 1
import pytest
from src.model.download_manager import DownloadManager
from unittest.mock import AsyncMock

from tcgdexsdk import SerieResume

@pytest.fixture
def fake_api_client(mocker):
    """Provide a fake api_client with async mocks for sets/cards."""

    class FakeSet:
        id = 'xy1'
        name = 'X & Y'
        serie = SerieResume('xy', 'XY', None)
        releaseDate = '16/01/2016'

        async def get_full_set(self):
            return FakeSet()

    # Mock for set list
    fake_list_sets = AsyncMock(return_value=[FakeSet()])

    # Mock for card resumes
    class Resume:
        id = "xy1-1"
        async def get_full_card(self):
            class Card:
                id = "xy1-1"
                name = "Bulbasaur"
                set = FakeSet()
                category = "Pokémon"
                rarity = "Common"
                localId = '1'
                illustrator = 'HYOGONOSUKE'

                variants={
                        'normal': True,
                        'holo': True,
                        'reverseHolo': False,
                        '1stEdition': False,
                        'wPromo': False
                        }
            return Card()
        
    async def fake_get_card(card_id):
        return await Resume().get_full_card()

    fake_list_cards = AsyncMock(return_value=[Resume()])
    fake_get_card = AsyncMock(side_effect=fake_get_card)

    # Build fake client manually instead of MagicMock
    class FakeClient:
        def __init__(self):
            self.list_sets = fake_list_sets
            self.list_cards = fake_list_cards
            self.get_card = fake_get_card

    return FakeClient()

@pytest.mark.asyncio
async def test_download_flow(fake_api_client):
    dm = DownloadManager(db_path=":memory:")
    dm.api_client = fake_api_client

    await dm.download_all()

    assert dm.db.n_done == 1
    fake_api_client.list_sets.assert_awaited_once()
    fake_api_client.list_cards.assert_awaited_once()
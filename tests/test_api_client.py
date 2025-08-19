import pytest
from src.model.api_client import APIClient

@pytest.fixture
def client():
    return APIClient()

@pytest.mark.asyncio
async def test_list_cards(client, monkeypatch):

    async def fake_listing():
        class FakeCard:
            id = 'xy1-1'
            name = 'Bulbasaur'
        return [FakeCard()]
    
    monkeypatch.setattr(client.client.card, 'list', fake_listing)
    result = await client.list_cards()

    assert result[0].id == 'xy1-1'
    
@pytest.mark.asyncio
async def test_get_full_card(client):
    class FakeResume:
        async def get_full_card(self):
            class Card:
                id = "xy1-1"
            return Card()
        
    card = await client.get_full_card(FakeResume())
    assert card.id == 'xy1-1'

@pytest.mark.asyncio
async def test_get_set_list(client, monkeypatch):

    async def fake_set_list():
        class FakeSetResume:
            async def get_full_set(self):
                class FakeSet:
                    id='xy1'
                return FakeSet()
        return [FakeSetResume()]
    
    monkeypatch.setattr(client.client.set, 'list', fake_set_list)
    result = await client.list_sets()

    assert result[0].id == 'xy1'

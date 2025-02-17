import config
from pokemontcgsdk import RestClient

def test_api_key_registered():
    assert RestClient.api_key == config.API_KEY

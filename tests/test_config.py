import config
import os
from pokemontcgsdk import RestClient

def test_api_key_registered():
    assert RestClient.api_key == config.API_KEY

def test_setlist_location():
    assert os.path.exists(config.SET_LIST_LOCATION)
import pytest
from src.pack_logic import Pack

@pytest.fixture(scope='session')
def pack_for_testing():
    return Pack('sv8')
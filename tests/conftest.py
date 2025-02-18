import pytest
from src.pack_logic import Pack

@pytest.fixture(scope='session')
def pack_for_testing():
    """Enter set code here to choose which set the pack will be drawn from"""
    return Pack('sv8')
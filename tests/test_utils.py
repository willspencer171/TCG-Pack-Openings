from src.utils import debug_message
from config import DEBUG

def test_debug_message():
    assert DEBUG
    debug_message('Hello, this is a debug test')

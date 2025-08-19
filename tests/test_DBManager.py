import pytest
from src.model.db_manager import DBManager
from tcgdexsdk import SerieResume, SetResume

from dataclasses import dataclass

@pytest.fixture
def db():
    return DBManager(':memory:')

@pytest.fixture
def fakeset():
    @dataclass
    class FakeSet:
        id = 'xy1'
        name = 'X & Y'
        serie = SerieResume('xy', 'XY', None)
        releaseDate = '16/01/2016'

    return FakeSet()

@pytest.fixture
def fakecard():
    @dataclass
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

# === Card Download Progress ===

def test_insert_card_progress(db):
    db.fill_progress_table("xy1-1")
    assert db.n_total == 1

def test_mark_done(db):
    db.fill_progress_table('xy1-1')
    db.mark_done('xy1-1')

    assert db.n_done == 1 and db.n_total == 1

def test_mark_error(db):
    db.fill_progress_table('xy1-2')
    db.mark_error('xy1-2')

    assert len(db.get_pending()) == 1

# === Insert Sets ===

def test_insert_set(db, fakeset):

    db.fill_sets_table(fakeset)

    assert db.n_sets == 1

# === Insert Cards ===

def test_insert_card(db, fakeset, fakecard):
    db.fill_sets_table(fakeset)
    db.insert_card(fakecard)

    assert db.n_cards == 1

# === Inventory ===

def test_add_to_inventory(db, fakeset, fakecard):
    db.fill_sets_table(fakeset)
    db.insert_card(fakecard)
    db.add_to_inventory(fakecard.id, 'normal')
    db.add_to_inventory(fakecard.id, 'normal')
    db.add_to_inventory(fakecard.id, 'holo')

    assert db.get_qty_for_card(fakecard.id, 'qty')[0][2] == 2   # Sort descending by qty
    assert db.get_qty_for_card(fakecard.id)[0][2] == 1          # Sort ascending by variant

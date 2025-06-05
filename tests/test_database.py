import src.model.db as db

def test_is_outdated():
    from datetime import datetime, timedelta

    # Test with a date more than 5 days ago
    outdated_date = datetime.now() - timedelta(days=6)
    assert db.is_outdated(outdated_date) is True

    # Test with a date exactly 5 days ago
    exact_date = datetime.now() - timedelta(days=5)
    assert db.is_outdated(exact_date) is True

    # Test with a date less than 5 days ago
    recent_date = datetime.now() - timedelta(days=4)
    assert db.is_outdated(recent_date) is False

def test_tables_exist():
    # Check if the tables were created successfully
    cursor = db.cursor
    tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    assert all([table[0] in ['cards', 'sets', 'metadata', 'sqlite_sequence'] for table in tables])

def test_populate_data():
    cursor = db.cursor
    sets = cursor.execute("SELECT * FROM sets").fetchall()
    cards = cursor.execute("SELECT * FROM cards").fetchall()

    assert len(sets) > 0, "Sets table should not be empty"
    assert len(cards) > 0, "Cards table should not be empty"
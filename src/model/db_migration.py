import hashlib

def get_card_qual_hash(card_id, quality):
    raw = f'{card_id}::{quality}'
    return int(hashlib.sha256(raw.encode()).hexdigest(), 16) % (10 ** 8)

def safe_rename_table(cursor, old_name, new_name):
    cursor.execute('''
        SELECT name FROM sqlite_master
        WHERE type='table' AND name=?
    ''', (new_name,))
    result = cursor.fetchone()

    if result is None:
        cursor.execute(f'ALTER TABLE {old_name} RENAME TO {new_name}')
    else:
        print(f'Table \'{new_name}\' already exists. Skipping rename.')

def create_backup(connection, cursor):
    safe_rename_table(cursor, 'cards', 'cards_old')
    safe_rename_table(cursor, 'sets', 'sets_old')
    safe_rename_table(cursor, 'metadata', 'metadata_old')
    connection.commit()

def migrate_records(connection, cursor):
    # Sets
    cursor.execute('SELECT DISTINCT set_id, name, series_name from sets_old')
    for id, name, series in cursor.fetchall():
        cursor.execute('''INSERT OR IGNORE INTO sets (set_id, name, series_name) VALUES (?, ?, ?)''', (id, name, series))
    
    # Cards
    cursor.execute('SELECT * FROM cards_old')
    for row in cursor.fetchall():
        card_id, set_id, name, rarity, supertype, subtypes_str, quality, image_small_url, image_large_url, price, artist, number, types_str = row

        card_quality_instance_id = get_card_qual_hash(card_id, quality)

        cursor.execute('''INSERT OR IGNORE INTO cards (card_id, set_id, name, rarity, supertype, quality, image_small_url, image_large_url, price, artist, number, card_quality_instance_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                       (card_id, set_id, name, rarity, supertype, quality, image_small_url, image_large_url, price, artist, number, card_quality_instance_id))

        # Types
        for t in (types_str or "").split(','):
            t = t.strip()
            if not t: 
                continue
            cursor.execute('INSERT OR IGNORE INTO types (name) VALUES (?)', (t,))
            cursor.execute('SELECT type_id FROM types WHERE name = ?', (t,))
            type_id = cursor.fetchone()[0]
            cursor.execute('INSERT INTO types_cards (type_id, card_quality_instance_id) VALUES (?, ?)', (type_id, card_quality_instance_id))
        
        # Subtypes
        for st in (subtypes_str or "").split(','):
            st = st.strip()
            if not st: 
                continue
            cursor.execute('INSERT OR IGNORE INTO subtypes (name) VALUES (?)', (st,))
            cursor.execute('SELECT subtype_id FROM subtypes WHERE name = ?', (st,))
            subtype_id = cursor.fetchone()[0]
            cursor.execute('INSERT INTO subtypes_cards (subtype_id, card_quality_instance_id) VALUES (?, ?)', (subtype_id, card_quality_instance_id))

    row = cursor.execute('SELECT * from metadata_old').fetchone()
    cursor.execute('''INSERT OR IGNORE INTO metadata (created_at, updated_at) VALUES (?, ?)''', (row[0], row[1]))

    connection.commit()
    cursor.execute('DROP TABLE IF EXISTS cards_old')
    cursor.execute('DROP TABLE IF EXISTS sets_old')
    cursor.execute('DROP TABLE IF EXISTS metadata_old')
    connection.commit()

from time import sleep
import sqlite3 as sql
from datetime import date, datetime
from http.client import IncompleteRead, RemoteDisconnected
from pokemontcgsdk.restclient import PokemonTcgException
import hashlib

from src.model.pack_logic import HashCard
from src.model.utils import debug_message
from config import DATABASE_LOCATION, SETS


def __all__():
    return ['create_tables', 'populate_data']

def get_card_qual_hash(card_id, quality):
    raw = f'{card_id}::{quality}'
    return int(hashlib.sha256(raw.encode()).hexdigest(), 16) % (10 ** 16)

def how_outdated(updated_at, sep='-') -> int:
    """Calculates how many days the database is outdated

    Args:
        updated_at (str): String of the format 'YYYY-MM-DD' or a datetime object

    Returns:
        int: Days since the last update
    """
    if sep == '-':
        updated_dt = (datetime.strptime(updated_at, '%Y-%m-%d')
                   if isinstance(updated_at, str) else updated_at)
    elif sep == '/':
        updated_dt = (datetime.strptime(updated_at, '%Y/%m/%d')
                   if isinstance(updated_at, str) else updated_at)
    return (date.today() - updated_dt.date()).days

def is_outdated(updated_at) -> bool:
    """Tells if the database is outdated

    Args:
        updated_at (datetime): The last time the database was updated

    Returns:
        bool: Returns True if the database is outdated by 30 days
    """
    return how_outdated(updated_at) >= 5

def create_tables():
    connection = sql.connect(DATABASE_LOCATION, detect_types=sql.PARSE_DECLTYPES | sql.PARSE_COLNAMES)
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS cards (
                        card_id TEXT PRIMARY KEY,
                        set_id TEXT,
                        name TEXT,
                        rarity TEXT,
                        supertype TEXT,
                        quality TEXT,
                        image_small_url TEXT,
                        image_large_url TEXT,
                        price REAL,
                        number TEXT,
                        artist TEXT,
                        card_quality_instance_id INTEGER,
                        FOREIGN KEY (set_id) REFERENCES sets(set_id)    
)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS sets (
                        set_id TEXT PRIMARY KEY,
                        name TEXT,
                        series_name TEXT,
                        image_logo TEXT,
                        image_symbol TEXT,
                        release_date DATE
)''')
    
    #Need to create an inventory thing here too
    cursor.execute('''CREATE TABLE IF NOT EXISTS card_inventory (
                        card_quality_instance_id INTEGER PRIMARY KEY,
                        count INTEGER
)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                        product_id INTEGER PRIMARY KEY,
                        name TEXT UNIQUE,
                        card_count INTEGER,
                        pack_count INTEGER
)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS product_inventory (
                        product_id INTEGER PRIMARY KEY,
                        count INTEGER,
                        FOREIGN KEY (product_id) REFERENCES products(product_id)

)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS product_set (
                        product_id INTEGER,
                        set_id TEXT,
                        FOREIGN KEY (product_id) REFERENCES products(product_id),
                        FOREIGN KEY (set_id) REFERENCES sets(set_id)
)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS types (
                        type_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE
)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS subtypes (
                        subtype_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE
)''')

    # Many-to-many mapping tables
    cursor.execute('''CREATE TABLE IF NOT EXISTS types_cards (
                        type_id INTEGER,
                        card_quality_instance_id INTEGER,
                        FOREIGN KEY (type_id) REFERENCES types(type_id),
                        FOREIGN KEY (card_quality_instance_id) REFERENCES card_inventory(card_quality_instance_id)
)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS subtypes_cards (
                        subtype_id INTEGER,
                        card_quality_instance_id INTEGER,
                        FOREIGN KEY (subtype_id) REFERENCES subtypes(subtype_id),
                        FOREIGN KEY (card_quality_instance_id) REFERENCES card_inventory(card_quality_instance_id)
)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS metadata (
                        created_at TEXT DEFAULT CURRENT_DATE,
                        updated_at TEXT DEFAULT "1990-01-01")''')
    cursor.execute('''INSERT OR IGNORE INTO metadata DEFAULT VALUES''')
    connection.commit()
    connection.close()

def update_db(cursor, connection, cards: list[HashCard], log_date=None):
    set_fields = [(s.id, s.name, s.series, s.images['logo'], s.images['symbol'], s.releaseDate) for s in SETS]

    cursor.executemany('INSERT OR IGNORE INTO sets (set_id, name, series_name, image_logo, image_symbol, release_date) VALUES (?, ?, ?, ?, ?, ?)', set_fields)
    
    if cards:
        for card in cards:
            for quality in card.qualities:
                card_quality_instance_id = get_card_qual_hash(card.id, quality)
                cursor.execute('''INSERT OR IGNORE INTO cards (card_id, set_id, name, rarity, supertype, quality, image_small_url, image_large_url, price, artist, number, card_quality_instance_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                        (card.id, card.set_id, card.name, card.rarity, card.supertype, quality, card.image_small_url, card.image_large_url, card.prices.get(quality, {}).get('market', 0.0), card.artist, card.number, card_quality_instance_id))

                for t in (card.types or []):
                    t = t.strip()
                    if not t: 
                        continue
                    cursor.execute('INSERT OR IGNORE INTO types (name) VALUES (?)', (t,))
                    cursor.execute('SELECT type_id FROM types WHERE name = ?', (t,))
                    type_id = cursor.fetchone()[0]
                    cursor.execute('INSERT INTO types_cards (type_id, card_quality_instance_id) VALUES (?, ?)', (type_id, card_quality_instance_id))

                for st in (card.subtypes or []):
                    st = st.strip()
                    if not st: 
                        continue
                    cursor.execute('INSERT OR IGNORE INTO subtypes (name) VALUES (?)', (st,))
                    cursor.execute('SELECT subtype_id FROM subtypes WHERE name = ?', (st,))
                    subtype_id = cursor.fetchone()[0]
                    cursor.execute('INSERT INTO subtypes_cards (subtype_id, card_quality_instance_id) VALUES (?, ?)', (subtype_id, card_quality_instance_id))
            
    if log_date:
        cursor.execute('''UPDATE metadata
                        SET updated_at = ?''', (log_date,))
    else:
        cursor.execute('''UPDATE metadata
                        SET updated_at = CURRENT_DATE''')
    
    connection.commit()

def insert_record(cursor, connection, table, fields, values: list):
    """Inserts a record into the specified table with the given fields and values."""
    if table == 'cards':
        values.append(get_card_qual_hash(values[0], values[5]))

    placeholders = ', '.join(['?'] * len(values))
    query = f'INSERT OR IGNORE INTO {table} ({", ".join(fields)}) VALUES ({placeholders})'
    cursor.execute(query, values)
    connection.commit()
    
def populate_data(attempts=0, pageSize=250):
    connection = sql.connect(DATABASE_LOCATION, detect_types=sql.PARSE_DECLTYPES | sql.PARSE_COLNAMES)
    cursor = connection.cursor()
    page = 1

    last_updated = cursor.execute('SELECT updated_at as "updated_at [date]" FROM metadata').fetchone()[0]
    with open('data/incomplete_read.log', 'r') as f:
        interrupted_str = f.read().strip()
        start_point = datetime.strptime(interrupted_str, '%Y-%m-%d') if interrupted_str != '0' else last_updated
    set_dates = [s.releaseDate for s in SETS
                     if datetime.strptime(s.releaseDate, '%Y/%m/%d') >= start_point]

    if len(set_dates) > 0:
        debug_message(f'Updating database from {start_point} onwards...')
        cards = []
        error_occurred = False
            
        while True:
            try:
                debug_message(f'Page: {page}, Page Size: {pageSize}')
                batch = HashCard.where(q=f'set.releaseDate:"{"\" OR set.releaseDate:\"".join(set_dates)}"',
                               page=page, pageSize=pageSize, orderBy='set.releaseDate,number')
            except (IncompleteRead, RemoteDisconnected, PokemonTcgException, KeyboardInterrupt) as e:
                debug_message('Failed to complete, will continue where it was left')
                if 'batch' in locals() and hasattr(batch[-1], 'set_id'):
                    s = [s for s in SETS if s.id == batch[-1].set_id][0]
                    interrupted_str = s.releaseDate.replace('/', '-')
                else:
                    interrupted_str = start_point.strftime('%Y-%m-%d')
                error_occurred = True
                debug_message(f'Error occurred: {e.__class__.__name__}')
                if isinstance(e, PokemonTcgException):
                    if '504' in bytes.decode(e.description):
                        debug_message('Server is busy, overloaded or down.')
                    elif bytes.decode(e.description) == '':
                        debug_message('Error message: Unexpected server-side error')
                elif isinstance(e, IncompleteRead):
                    debug_message(f'Error message: {e.partial}')
                else:
                    debug_message(f'Error message: {e.errno}')
                break
            
            if not batch:
                break
            cards.extend(batch)
            if len(batch) < pageSize:
                break
            page += 1

        if not error_occurred:
            update_db(cursor, connection, cards)
            with open('data/incomplete_read.log', 'w') as f:
                f.write('0')
        else:
            update_db(cursor, connection, cards, interrupted_str)
            with open('data/incomplete_read.log', 'w') as f:
                f.write(f'{interrupted_str}')
            
            if attempts >= 3:
                debug_message('Failed to update database after 3 reattempts, exiting...')
                connection.close()
                return
            sleep(5)
            populate_data(attempts + 1, pageSize=pageSize-50)

    else:
        debug_message('Database is up to date, no need to update.')

    connection.close()

def fetch_cards(id: list[str] = None, set_id: list[str] = None, set_id_like: list[str] = None, name: list[str] = None, name_like: list[str] = None,
                set_name: list[str] = None, rarity: list[str] = None, not_rarity: list[str] = None, rarity_not_null: bool = True, rarity_like: list[str] = None,
                rarity_not_like: list[str] = None, supertype: list[str] = None, supertype_not: list[str] = None, subtypes:list[str] = None, price: list[float] = None,
                price_range: tuple[float, float] = None, price_lt: float = None, price_gt: float = None,
                artist_like: list[str] = None, types: list[str] = None, quality: list[str] = None, series: list[str] = None, set_release: list[datetime] = None) -> list[HashCard]:
    connection = sql.connect(DATABASE_LOCATION, detect_types=sql.PARSE_DECLTYPES | sql.PARSE_COLNAMES)
    cursor = connection.cursor()
    query = 'SELECT cards.*, types.name, subtypes.name FROM cards'
    query += ' JOIN subtypes_cards ON cards.card_quality_instance_id = subtypes_cards.card_quality_instance_id'
    query += ' JOIN subtypes ON subtypes_cards.subtype_id = subtypes.subtype_id'
    query += ' JOIN types_cards ON cards.card_quality_instance_id = types_cards.card_quality_instance_id'
    query += ' JOIN types ON types_cards.type_id = types.type_id'
    where_clauses = ['1=1']
    params = []
    if set_id:
        for sid in set_id:
            debug_message(f'Adding set_id: {sid}')
            where_clauses.append('set_id = ?')
            params.append(sid)
    if set_id_like:
        for sid in set_id_like:
            debug_message(f'Adding set_id_like: {sid}')
            where_clauses.append('set_id LIKE ?')
            params.append(f'{sid}_g')
    if id:
        for card_id in id:
            debug_message(f'Adding card_id: {card_id}')
            where_clauses.append('card_id = ?')
            params.append(card_id)
    if name:
        for card_name in name:
            debug_message(f'Adding card_name: {card_name}')
            where_clauses.append('name = ?')
            params.append(card_name)
    if name_like:
        for card_name in name_like:
            debug_message(f'Adding card_name_like: {card_name}')
            where_clauses.append('name LIKE ?')
            params.append(f'%{card_name}%')
    if set_name:
        for s_name in set_name:
            debug_message(f'Adding set_name: {s_name}')
            where_clauses.append('set_name = ?')
            params.append(s_name)
    if rarity:
        for r in rarity:
            debug_message(f'Adding rarity: {r}')
            where_clauses.append('rarity = ?')
            params.append(r)
    if not_rarity:
        for r in not_rarity:
            debug_message(f'Adding not_rarity: {r}')
            where_clauses.append('rarity != ?')
            params.append(r)
    if rarity_not_null:
        debug_message('Adding rarity_not_null condition')
        where_clauses.append('rarity IS NOT NULL')
    if rarity_like:
        for r in rarity_like:
            debug_message(f'Adding rarity_like: {r}')
            where_clauses.append('rarity LIKE ?')
            params.append(f'%{r}%')
    if rarity_not_like:
        for r in rarity_not_like:
            debug_message(f'Adding rarity_not_like: {r}')
            where_clauses.append('rarity NOT LIKE ?')
            params.append(f'%{r}%')
    if supertype:
        for st in supertype:
            debug_message(f'Adding supertype: {st}')
            where_clauses.append('supertype = ?')
            params.append(st)
    if supertype_not:
        for st in supertype_not:
            debug_message(f'Adding supertype_not: {st}')
            where_clauses.append('supertype != ?')
            params.append(st)
    if subtypes:
        for subtype in subtypes:
            debug_message(f'Adding subtype: {subtype}')
            where_clauses.append('subtypes.name = ?')
            params.append(f'{subtype}')
    if price:
        for p in price:
            debug_message(f'Adding price: {p}')
            where_clauses.append('price = ?')
            params.append(p)
    if price_range:
        debug_message(f'Adding price_range: {price_range}')
        where_clauses.append('price BETWEEN ? AND ?')
        params.extend(price_range)
    if price_lt is not None:
        debug_message(f'Adding price_lt: {price_lt}')
        where_clauses.append('price < ?')
        params.append(price_lt)
    if price_gt is not None:
        debug_message(f'Adding price_gt: {price_gt}')
        where_clauses.append('price > ?')
        params.append(price_gt)
    if artist_like:
        for a in artist_like:
            debug_message(f'Adding artist_like: {a}')
            where_clauses.append('artist LIKE ?')
            params.append(f'%{a}%')
    if types:
        debug_message(f'Adding types: {types}')
        where_clauses.append('types.name IN (' + ','.join(['?'] * len(types)) + ')')
        params.append(types)
    if quality:
        for q in quality:
            debug_message(f'Adding quality: {quality}')
            where_clauses.append('quality = ?')
            params.append(q)
    if series:
        for s in series:
            debug_message(f'Adding series: {s}')
            where_clauses.append('sets.series = ?')
            params.append(s)
    if set_release:
        for release in set_release:
            release = release.strftime('%Y-%m-%d')
            debug_message(f'Adding set_release: {release}')
            where_clauses.append('sets.release_date = ?')
            params.append(release)
    if series or set_release:
        query += ' JOIN sets ON cards.set_id = sets.id'
    
    query += ' WHERE ' + ' AND '.join(where_clauses)
    debug_message(f'Executing query: {query} with params: {params}')
    result = cursor.execute(query, params).fetchall()
    connection.close()
    return result

def parse_date(date_str):
    """Parses a date string in the format 'YYYY-MM-DD' to a datetime object."""
    return datetime.strptime(date_str.decode('utf-8'), '%Y-%m-%d')

sql.register_converter('date', parse_date)

from pokemontcgsdk import Set
import sqlite3 as sql
from datetime import date, datetime
from http.client import IncompleteRead, RemoteDisconnected
from pokemontcgsdk.restclient import PokemonTcgException

from src.model.pack_logic import HashCard
from src.model.utils import debug_message


def __all__():
    return ['create_tables', 'populate_data']

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
        bool: Returns True if the database is outdated by 5 days
    """
    return how_outdated(updated_at) >= 5

def create_tables():
    cursor.execute('''CREATE TABLE IF NOT EXISTS cards (
                        id TEXT PRIMARY KEY,
                        name TEXT,
                        set_id TEXT,
                        set_name TEXT,
                        rarity TEXT,
                        supertype TEXT,
                        subtypes TEXT,
                        quality TEXT,
                        image_small_url TEXT,
                        price REAL,
                        artist TEXT,
                        number TEXT,
                        types TEXT,
                        FOREIGN KEY (set_id) REFERENCES sets(id)
)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS sets (
                        id TEXT PRIMARY KEY,
                        name TEXT,
                        series TEXT
)''')
    
    #Need to create an inventory thing here too

    cursor.execute('''CREATE TABLE IF NOT EXISTS metadata (
                        created_at TEXT DEFAULT CURRENT_DATE,
                        updated_at TEXT DEFAULT "1990-01-01")''')
    cursor.execute('''INSERT OR IGNORE INTO metadata DEFAULT VALUES''')
    
def populate_data():
    page = 1
    last_updated = cursor.execute('SELECT updated_at as "updated_at [date]" FROM metadata').fetchone()[0]
    with open('data/incomplete_read.log', 'r') as f:
        interrupted_str = f.read().strip()
        start_point = datetime.strptime(interrupted_str, '%Y-%m-%d') if interrupted_str != '0' else last_updated

    if is_outdated(start_point):
        debug_message(f'Updating database from {start_point} onwards...')
        sets = Set.all()
        set_dates = [s.releaseDate for s in sets
                     if datetime.strptime(s.releaseDate, '%Y/%m/%d') >= start_point]
        cards = []
        error_occurred = False
            
        while True:
            try:
                batch = HashCard.where(q=f'set.releaseDate:"{"\" OR set.releaseDate:\"".join(set_dates)}"',
                               page=page, pageSize=250, orderBy='set.releaseDate,number')
            except (IncompleteRead, RemoteDisconnected, PokemonTcgException, KeyboardInterrupt):
                debug_message('Failed to complete, will continue where it was left')
                if 'batch' in locals() and hasattr(batch[0], 'set') and hasattr(batch[0].set, 'releaseDate'):
                    interrupted_str = batch[0].set.releaseDate.replace('/', '-') if batch else start_point.strftime('%Y-%m-%d')
                error_occurred = True
                break
            
            if not batch:
                break
            cards.extend(batch)
            if len(batch) < 250:
                break
            page += 1

        if not error_occurred:
            with open('data/incomplete_read.log', 'w') as f:
                f.write('0')
        else:
            with open('data/incomplete_read.log', 'w') as f:
                f.write(f'{interrupted_str}')
        
        set_fields = [(s.id, s.name, s.series) for s in sets]
        card_fields = [(card.id, card.name, card.set_id, card.set_name, card.rarity,
                        card.supertype, ','.join(card.subtypes), card.quality, card.image_small_url,
                        card.price, card.artist, card.number, ','.join(card.types) if isinstance(card.types, list) else card.types) for card in cards]

        cursor.executemany('INSERT OR IGNORE INTO sets (id, name, series) VALUES (?, ?, ?)', set_fields)
        cursor.executemany(f'''INSERT OR IGNORE INTO cards (id, name, set_id, set_name, rarity,
        supertype, subtypes, quality, image_small_url, price, artist, number, 
        types) VALUES ({','.join(['?'] * len(card_fields[0]))})''',
        card_fields)
    
        cursor.execute('''UPDATE metadata
                   SET updated_at = CURRENT_DATE''')
        
        connection.commit()
    else:
        debug_message('Database is up to date, no need to update.')

def fetch_cards(id: list[str] = None, set_id: list[str] = None, set_id_like: list[str] = None, name: list[str] = None, name_like: list[str] = None,
                set_name: list[str] = None, rarity: list[str] = None, not_rarity: list[str] = None, rarity_not_null: bool = True, rarity_like: list[str] = None,
                rarity_not_like: list[str] = None, supertype: list[str] = None, supertype_not: list[str] = None, subtypes:list[str] = None, price: list[float] = None,
                price_range: tuple[float, float] = None, price_lt: float = None, price_gt: float = None,
                artist_like: list[str] = None, types: list[str] = None, quality: list[str] = None, series: list[str] = None, set_release: list[datetime] = None) -> list[HashCard]:
    query = 'SELECT cards.* FROM cards'
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
            where_clauses.append('id = ?')
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
            where_clauses.append('subtypes = ?')
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
        where_clauses.append('types IN (' + ','.join(['?'] * len(types)) + ')')
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
    return cursor.execute(query, params).fetchall()

def parse_date(date_str):
    """Parses a date string in the format 'YYYY-MM-DD' to a datetime object."""
    return datetime.strptime(date_str.decode('utf-8'), '%Y-%m-%d')

sql.register_converter('date', parse_date)
connection = sql.connect('data/pokemon.db', detect_types=sql.PARSE_COLNAMES)
cursor = connection.cursor()

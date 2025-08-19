import sqlite3 as sql
from config import DATABASE_LOCATION
import tcgdexsdk as tcgdex

from typing import Literal

class DBManager():
    def __init__(self, path=DATABASE_LOCATION):
        self.conn = sql.connect(path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._init_db()
    
    def _init_db(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS cards_progress(
                        card_id TEXT PRIMARY KEY,
                        status TEXT,
                        last_attempt TEXT
                        )
        """)
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS cards(
                        card_id TEXT PRIMARY KEY,
                        set_id TEXT,
                        name TEXT,
                        rarity TEXT,
                        supertype TEXT,
                        number TEXT,
                        artist TEXT,
                        FOREIGN KEY (set_id) REFERENCES sets(set_id)
                        )
        """)
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS sets(
                        set_id TEXT PRIMARY KEY,
                        name TEXT,
                        series_name TEXT,
                        release_date DATE
                        )
        """)
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS variants(
                        variant TEXT PRIMARY KEY
                        )
        """)
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS cards_variants(
                        card_id TEXT,
                        variant TEXT,
                        PRIMARY KEY (card_id, variant),
                        FOREIGN KEY (card_id) REFERENCES cards(card_id),
                        FOREIGN KEY (variant) REFERENCES variants(variant)
                        )
        """)
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS card_inventory(
                        card_id TEXT NOT NULL,
                        variant TEXT NOT NULL,
                        quantity INTEGER NOT NULL DEFAULT 0 CHECK (quantity >=0),
                        PRIMARY KEY (card_id, variant)
                        FOREIGN KEY (card_id, variant) REFERENCES cards_variants(card_id, variant)
                        )
        """)
        self.conn.commit()
    
    def fill_progress_table(self, card_id: str):
        self.conn.execute(
            "INSERT OR IGNORE INTO cards_progress(card_id, status) VALUES (?, 'pending')", 
                          (card_id,)
                          )
        self.conn.commit()

    def fill_sets_table(self, set: tcgdex.Set):
        self.conn.execute("""
            INSERT OR IGNORE INTO sets(
                        set_id, name, series_name, release_date
                        ) VALUES (?,?,?,?)""",
                        (set.id, set.name, getattr(set.serie, 'name'), set.releaseDate))
        self.conn.commit()

    def mark_done(self, card_id: str):
        self.conn.execute(
            "UPDATE cards_progress SET status='done', last_attempt=datetime('now') WHERE card_id=?",
                        (card_id,)
                        )
        self.conn.commit()
        
    def mark_error(self, card_id: str):
        self.conn.execute("UPDATE cards_progress SET status='error', last_attempt=datetime('now') WHERE card_id=?",
                          (card_id,))
        self.conn.commit()

    def get_pending(self, limit=50):
        return self.conn.execute(
            """SELECT card_id FROM cards_progress WHERE status!='done' LIMIT ?""",
            (limit,)).fetchall()
    
    @property
    def n_done(self):
        return self.conn.execute(
            "SELECT count(*) FROM cards_progress WHERE status='done'"
        ).fetchone()[0]

    @property
    def n_total(self):
        return self.conn.execute(
            "SELECT count(*) FROM cards_progress"
        ).fetchone()[0]
    
    @property
    def n_sets(self):
        return self.conn.execute(
            "SELECT count(*) FROM sets"
        ).fetchone()[0]
    
    @property
    def n_cards(self):
        return self.conn.execute(
            "SELECT count(*) FROM cards"
        ).fetchone()[0]
    
    def insert_variants(self, variants: list[str]):
        self.conn.executemany(
            "INSERT OR IGNORE INTO variants (variant) VALUES (?)",
            [(v,) for v in variants]
        )
        self.conn.commit()
    
    def insert_card_variants(self, card_id: str, variant: str):
        self.conn.execute(
            "INSERT OR IGNORE INTO cards_variants (card_id, variant) VALUES (?, ?)",
            (card_id, variant)
        )
        self.conn.commit()
    
    def insert_card(self, card: tcgdex.Card):
        self.conn.execute("""INSERT OR REPLACE INTO cards
                          (card_id, set_id, name, rarity, supertype, number, artist)
                          VALUES (?,?,?,?,?,?,?)""",
                          (card.id,
                          card.set.id,
                          card.name,
                          card.rarity,
                          card.category,
                          card.localId,
                          card.illustrator)
                          )
        
        variants = card.variants
        variant_names = [k for k, v in variants.items() if v]
        self.insert_variants(variant_names)
        for v in variant_names:
            self.insert_card_variants(card.id, v)
        self.conn.commit()
    
    def add_to_inventory(self, card_id: str, variant: str):
        self.conn.execute(
            """
            INSERT INTO card_inventory (card_id, variant, quantity)
            VALUES (?,?,1)
            ON CONFLICT (card_id, variant)
            DO UPDATE SET quantity = quantity + excluded.quantity
            """,
            (card_id, variant))
        self.conn.commit()

    def remove_from_inventory(self, card_id: str, variant: str):
        self.conn.execute("""
        UPDATE card_inventory
        SET quantity = quantity - 1
        WHERE card_id=? AND variant=?
        """, (card_id, variant))
        self.conn.execute("""
            DELETE FROM card_inventory
            WHERE card_id=? AND variant=? AND quantity <= 0
        """, (card_id, variant))
        self.conn.commit()

    def get_qty_for_card(self, card_id: str, order_by: Literal['variant', 'qty']='variant'):
        if order_by == 'variant':
            result = self.conn.execute(
            """SELECT card_id, variant, SUM(quantity) AS qty
            FROM card_inventory
            WHERE card_id=?
            GROUP BY card_id, variant
            ORDER BY variant ASC""",
            (card_id,)
        ).fetchall()
        
        elif order_by == 'qty':
            result = self.conn.execute(
            """SELECT card_id, variant, SUM(quantity) AS qty
            FROM card_inventory
            WHERE card_id=?
            GROUP BY card_id, variant
            ORDER BY qty DESC""",
            (card_id,)
        ).fetchall()

        return result
    
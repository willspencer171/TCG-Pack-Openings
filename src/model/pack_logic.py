from __future__ import annotations

from src.model.utils import debug_message, download_pack_images, show_images
import config

import random
import asyncio

from pokemontcgsdk import QueryBuilder, Set
from dataclasses import dataclass


@dataclass
class HashCard:
    """HashCard dataclass ensures a hash table-like object can be used to
    keep track of obtained cards from pulls in the future"""

    id: str
    name: str
    set_id: str
    rarity: str
    supertype: str
    subtypes: list[str]
    image_small_url: str
    image_large_url: str
    artist: str
    number: str
    types: list[str]
    quality: str = 'normal'
    price: float = 0.0
    qualities = [
        "normal",
        "holofoil",
        "reverseHolofoil",
        "1stEditionNormal",
        "1stEditionHolofoil",
    ]
    prices: dict[str, dict[str, float]] = None
    RESOURCE = "cards"

    def __hash__(self):
        return hash(self.id + self.quality)

    def __eq__(self, other):
        return self.id == other.id

    @staticmethod
    def find(id) -> 'HashCard':
        from src.model.db import fetch_cards
        rows = fetch_cards(id=[id])
        if rows:
            return HashCard.from_db_row(rows[0])
        return None

    @staticmethod
    def where(id: list[str] = None, set_id: list[str] = None, set_id_like: list[str] = None, name: list[str] = None, name_like: list[str] = None,
                set_name: list[str] = None, rarity: list[str] = None, not_rarity: list[str] = None, rarity_not_null: bool = True, rarity_like: list[str] = None,
                rarity_not_like: list[str] = None, supertype: list[str] = None, supertype_not: list[str] = None, subtypes:list[str] = None, price: list[float] = None,
                price_range: tuple[float, float] = None, price_lt: float = None, price_gt: float = None,
                artist_like: list[str] = None, types: list[str] = None, quality: list[str] = None, series: list[str] = None,
                q:str=None, **kwargs) -> list['HashCard']:
        if q:
            return QueryBuilder(HashCard, HashCard.transform).where(q=q, **kwargs)

        from src.model.db import fetch_cards
        rows = fetch_cards(
            id=id,
            set_id=set_id,
            set_id_like=set_id_like,
            set_name=set_name,
            name=name,
            name_like=name_like,
            rarity=rarity,
            not_rarity=not_rarity,
            rarity_not_null=rarity_not_null,
            rarity_like=rarity_like,
            rarity_not_like=rarity_not_like,
            supertype=supertype,
            supertype_not=supertype_not,
            subtypes=subtypes,
            price=price,
            price_range=price_range,
            price_lt=price_lt,
            price_gt=price_gt,
            artist_like=artist_like,
            types=types,
            quality=quality,
            series=series
        )
        return [HashCard.from_db_row(row) for row in rows]

    @staticmethod
    def all() -> list['HashCard']:
        debug_message("Fetching all cards from the database. May take a while...")
        return QueryBuilder(HashCard, HashCard.transform).all()

    @staticmethod
    def transform(response: dict):
        this_quals = []
        for qual in HashCard.qualities:
            if response.get("tcgplayer", {}).get("prices", {}).get(qual):
                response["tcgplayer"]["prices"][qual] = {
                    key: round(
                        val * config.CURRENCY_CONVERSIONS[config.APP_CURRENCY], 2
                    )
                    for key, val in response["tcgplayer"]["prices"].pop(qual).items()
                    if val
                }
                this_quals.append(qual)

        if len(this_quals) == 0:
            this_quals.append("normal")

        response['set_id'] = response.get('set', {}).get('id', '')
        response['series'] = response.get('set', {}).get('series', 'Other')
        response['image_small_url'] = response.get('images', {}).get('small', '')
        response['image_large_url'] = response.get('images', {}).get('large', '')
        response['artist'] = response.get('artist', '')
        response['types'] = response.get('types', [])
        response['subtypes'] = response.get('subtypes', [])
        response['rarity'] = response.get('rarity', 'None')
        response['supertype'] = response.get('supertype', 'None')
        response['id'] = response.get('id', '')
        response['number'] = response.get('number', '')

        response['qualities'] = this_quals
        response['prices'] = response.get('tcgplayer', {}).get('prices', {})
        return response
    
    @classmethod
    def from_db_row(cls, row: tuple) -> HashCard:
        (id, set_id, name, rarity, supertype, 
         quality, img_sml, img_lge, 
         price, number, artist, _, types, subtypes) = row
        
        return cls(
            id=id,
            name=name,
            set_id=set_id,
            rarity=rarity,
            supertype=supertype,
            subtypes=subtypes,
            quality=quality,
            image_small_url=img_sml,
            image_large_url=img_lge,
            price=price,
            artist=artist,
            number=number,
            types=types,
        )

class Pack:
    ### Should be an abstract class implemented by each set? Maybe?
    ### Or just change the number of cards if it's a promo set

    # What does a pack need to have?
    # 1 energy card
    # 9 Other cards
    # Last card is guaranteed at least rare (rank 3)

    def __init__(self, set_id, ten_pack=False):
        self.set_id = set_id
        self.ten_pack = ten_pack
        self.set: Set = Set.find(set_id)
        self.pack_items: list[HashCard | None] = []
        self.available: list[HashCard | None]
        self.pick_cards()

    def __str__(self):
        return f"{self.set.name}"

    def pick_cards(self):
        debug_message(f"Fetching cards from {self.set.name}...")
        # Don't want energies if they're basic, we'll find them later
        self.available = HashCard.where(set_id=[self.set_id])

        if len(self.available) != 0:
            if any(
                [s in [self.set.id + "gg", self.set.id + "tg"] for s in config.setlist]
            ):
                debug_message("Adding gallery set")
                self.available += HashCard.where(set_id_like=[self.set_id])
            debug_message("Set cards retrieved!")
            high_rarity = [card for card in self.available if 
                           any(card.rarity in r for r in config.ranking_tiers[3:])]
        else:
            debug_message("Set has no rarity info, probs a promo")
            self.available = HashCard.where(set_id=[self.set_id], rarity_not_null=False)
            high_rarity = self.available

        if self.ten_pack:
            n_packs = 10
        else:
            n_packs = 1

        # Now we find the basic energies from the series
        energies = HashCard.where(series=[self.set.series], supertype=["Energy"], 
                                  subtypes=["Basic"], rarity_not_like=["Secret", "Hyper", "Holo"])

        self.available = [card for card in self.available if card not in energies]

        # If we don't find any basic energies, we can search through the series
        # around the current one

        if len(energies) > 0:
            debug_message("Basic energies found")
        else:
            debug_message(f"No energies found in series {self.set.series}")
            ### Search through series around
            match self.set.series:
                case "POP":
                    energies = HashCard.where(
                        series=['EX'], supertype=["Energy"], subtypes=["Basic"], rarity_not_like=['Holo'],
                    )

                case "Other":
                    energies = HashCard.where(
                        series=["Sword & Shield"], supertype=["Energy"], subtypes=["Basic"], 
                        rarity_not_like=["Secret"]
                    )

                case "Platinum":
                    energies = HashCard.where(
                        series=["Diamond & Pearl"], supertype=["Energy"], subtypes=["Basic"]
                    )

        debug_message(f"Got {len(energies)} energies")
        debug_message(
            f"Got {len(self.available)} cards, with {len(high_rarity)} high rank"
        )

        for _ in range(n_packs):
            # Add Energy card for first card
            self.pack_items.append(random.choice(energies))

            # Pick 9 cards
            self.pack_items += sorted(
                Pack._draw_random(self.available, 8),
                key=lambda x: config.RARITY_RANKING[x.rarity]
                + HashCard.qualities.index(x.quality),
            ) + Pack._draw_random(high_rarity, 1)

        asyncio.run(self.get_pack_images())

    @staticmethod
    def _draw_random(card_pool: list[HashCard], k=1):
        weights = config.RARITY_PROBABILITIES
        card_ranks = [
            weights[card.rarity] * 0.25
            if card.supertype == "Trainer"
            else weights[card.rarity]
            for card in card_pool
        ]

        cards = random.choices(card_pool, weights=card_ranks, k=k)
        return cards

    async def get_pack_images(self):
        pack_image_urls = [card.image_small_url for card in self.pack_items]
        self.image_data = await download_pack_images(pack_image_urls)

    async def show_pack_images(self):
        await show_images(self.image_data[::-1])

    def print_pack(self):
        for card in self.pack_items:
            print(card.name, card.rarity, card.quality, sep=" -- ")

    def __len__(self):
        return len(self.pack_items)

    def __iter__(self):
        yield from self.pack_items

    def __getitem__(self, index):
        return self.pack_items[index]

    def __hash__(self):
        return hash(self.set_id)

    def __eq__(self, other):
        return self.set_id == other.set_id


class PromoPack(Pack):
    @staticmethod
    def _draw_random():
        raise NotImplementedError

    def pick_cards(self):
        # 4 cards in pack
        pass

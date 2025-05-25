from __future__ import annotations  # Deprecated in Python 3.14

from src.model.utils import debug_message, download_pack_images, show_images
import config

import random
import asyncio
import numpy as np

from pokemontcgsdk import Card, QueryBuilder, Set
from dataclasses import dataclass


@dataclass
class HashCard(Card):
    """HashCard dataclass ensures a hash table-like object can be used to
    keep track of obtained cards from pulls in the future"""

    quality: str
    qualities = [
        "normal",
        "holofoil",
        "reverseHolofoil",
        "1stEditionNormal",
        "1stEditionHolofoil",
    ]

    def __hash__(self):
        return hash(self.id + self.quality)

    def __eq__(self, other):
        return self.id == other.id

    @staticmethod
    def find(id) -> HashCard:
        return QueryBuilder(HashCard, HashCard.transform).find(id)

    @staticmethod
    def where(**kwargs) -> list[HashCard]:
        return QueryBuilder(HashCard, HashCard.transform).where(**kwargs)

    @staticmethod
    def all() -> list[HashCard]:
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

        this_quals = np.array(this_quals)

        if this_quals.size != 0:
            weights = list(range(1, this_quals.size + 1))[::-1]
            response["quality"] = random.choices(this_quals, weights=weights)[0]
        else:
            response["quality"] = response.get("quality", "normal")
        return response

    @property
    def price(self):
        return getattr(
            getattr(
                getattr(getattr(self, "tcgplayer", None), "prices", None),
                self.quality,
                None,
            ),
            "market",
            0.0,
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
        query = f"set.id:{self.set_id} rarity:*"
        self.available = HashCard.where(q=query)

        if len(self.available) != 0:
            if any(
                [s in [self.set.id + "gg", self.set.id + "tg"] for s in config.setlist]
            ):
                debug_message("Adding gallery set")
                self.available += HashCard.where(q=f"set.id:{self.set_id}*g rarity:*")
            debug_message("Set cards retrieved!")
            high_rarity = [
                card
                for card in self.available
                if config.RARITY_RANKING[card.rarity] >= 2
            ]
        else:
            debug_message("Set has no rarity info, probs a promo")
            self.available = HashCard.where(q=f"set.id:{self.set_id}")
            high_rarity = self.available

        if self.ten_pack:
            n_packs = 10
        else:
            n_packs = 1

        # Now we find the basic energies from the series
        query = (
            f'set.series:"{self.set.series}" supertype:energy subtypes:basic '
            "-rarity:*secret* -rarity:*hyper* -rarity:*holo*"
        )
        energies = HashCard.where(q=query)

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
                        q=(
                            'set.series:"EX" supertype:energy subtypes:basic -rarity:*holo*'
                        )
                    )

                case "Other":
                    energies = HashCard.where(
                        q=(
                            'set.series:"Sword & Shield" supertype:energy '
                            "subtypes:basic -rarity:*secret*"
                        )
                    )

                case "Platinum":
                    energies = HashCard.where(
                        q=(
                            'set.series:"Diamond & Pearl" supertype:energy subtypes:basic'
                        )
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
                + HashCard.qualities.index(x.quality)
                + random.randint(-2, 2),
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
        pack_image_urls = [card.images.small for card in self.pack_items]
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

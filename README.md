# Pokémon Trading Card Game Pack Simulator

## Project Description

A small project that I've been putting on the backburner for a little while now. I like Pokémon and I like collecting Pokémon cards. However, with card packs being at least £4.29 each, I'd like to satiate my hunger for more cards without actually spending money. Hence, a simulator.

This uses the [Pokémon TCG API](pokemontcg.io) to generate a pack from a chosen set and open it. The test-driven approach I've used helps with structuring the package and running tests for it using Pytest. I aim to use as much good practice as possible throughout.

## Project To-Do List

Since this is a WIP project, here is a list of things I'd like to get done.

- ~~Get cards using the pokemontcg.io Python API~~
- ~~Generate a pack of 10 cards~~
- ~~"Open" that pack by fetching and showing images~~
- ~~Create a GUI for the pack opening procedure~~
- ~~Keep an inventory of which packs have been opened and what cards have been obtained~~
  - Do I need to come back to this one day?
  - Been working on this the most. Not bad at the moment
- Potentially introduce a currency or time lock so I don't lose the magic of opening packs
- Balancing the odds of getting rare cards

## This is something I'll come back to

This is because the TCG Guru API (and its parent website) are overwhelmed, making development difficult and clunky. As such, I might come back to this either once traffic slows, or when I've decided I want to restart and migrate to a different API (looking at you [TCGDex](https://tcgdex.dev/sdks/python))

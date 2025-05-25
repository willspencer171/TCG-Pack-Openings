from src.controller import Controller
import sys

if __name__ == "__main__":
    args = sys.argv[1:]
    controller = Controller()
    controller.run(args[0], ten_pack=False, rarity_difficulty=3)

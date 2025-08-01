from src.controller import Controller
import sys

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 1:
        print("Usage: python main.py <set_id> [ten_pack] [rarity_difficulty]")
        sys.exit(1)
    set_id = args[0]
    ten_pack = bool(int(args[1])) if len(args) >= 2 and args[1].isdigit() else False
    rarity_difficulty = int(args[2]) if len(args) >= 3 and args[2].isdigit() else 3

    controller = Controller()
    controller.run(set_id, ten_pack=ten_pack, rarity_difficulty=rarity_difficulty)

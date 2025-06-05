from src.controller import Controller
import sys

if __name__ == "__main__":
    args = sys.argv[1:]
    print(args)
    controller = Controller()
    controller.run(args[0], ten_pack=bool(int(args[1])) if len(args) >= 2 and args[1].isdigit() else False, 
                   rarity_difficulty=int(args[2]) if len(args) >= 3 and args[2].isdigit() else 3)

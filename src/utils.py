def debug_message(message):
    from config import DEBUG
    if DEBUG:
        print(f"\033[1;32[DEBUG] {message}")

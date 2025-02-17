def debug_message(message, type='debug'):
    from config import DEBUG
    if DEBUG:
        if type == 'debug':
            print(f"\033[34m[DEBUG] {message}")
        elif type == 'error':
            print(f"\033[31m [ERROR] {message}")
            quit()  ### Maybe this will mean return to search in the future

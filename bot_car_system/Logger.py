
from datetime import datetime

def info(text):
    text = f'{datetime.now()} | info | {text}'
    print(f'\033[92m{text}\033[00m')

def warning(text):
    text = f'{datetime.now()} | warning | {text}'
    print(f"\033[33m{text}\033[0m")

def error(text):
    text = f'{datetime.now()} | error | {text}'
    print(f'\033[91m{text}\033[00m')

def extra(text):
    text = f'{datetime.now()} | extra | {text}'
    print(f'\033[35m{text}\033[00m')

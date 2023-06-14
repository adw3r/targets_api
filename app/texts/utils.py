from random import choice
from string import ascii_letters, digits


async def generate_text(length: int = 6, sequence=ascii_letters + digits):
    return ''.join([choice(sequence) for _ in range(length)])

import random


def roll(number, sides):
    rolls = [random.randint(1,sides) for _ in range(number)]

    return sum(rolls)

import csv

import random


animals = []


with open(
    "data/animals.csv",
    encoding="utf-8"
) as file:

    reader = csv.DictReader(file)

    for row in reader:

        animals.append(row)


def get_random_animal(level):

    filtered = [

        animal

        for animal in animals

        if animal["level"] == level

    ]

    return random.choice(filtered)

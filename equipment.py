import json
import os

config = json.load(open(os.environ["CHARGEN_CONFIG"]))

EQUIPMENT_TABLE = {}


def load_equipment():
    with open(config["equipment_file"]) as equipment_data:
        for line in equipment_data:
            split_line = line.split(":")

            if len(split_line) != 2:
                continue

            key, equipment = split_line
            character_class, gold_roll = key.split(",")
            gold_roll = int(gold_roll)
            equipment = [e.strip() for e in equipment.split(",")]

            EQUIPMENT_TABLE[character_class, gold_roll] = equipment


def get_equipment(character_class, equipment_roll):
    if character_class in ["elf", "dwarf", "halfling"]:
        class_table = "fighter"
    else:
        class_table = character_class

    equipment = EQUIPMENT_TABLE[class_table, equipment_roll]

    if character_class in ["elf", "magic-user"]:
        equipment.append("spellbook")

    return equipment

load_equipment()


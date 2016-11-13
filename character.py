import json
import os
import os.path

import dice
import equipment

config = json.load(open(os.environ["CHARGEN_CONFIG"]))


class Character(dict):
    VALID_CLASSES = set(["cleric", "fighter", "magic-user", "thief", "elf", "dwarf", "halfling"])
    VALID_STATES = set(["new", "has-stats", "has-class", "done"])

    HP_DICE = {
        "cleric": 6,
        "fighter": 8,
        "magic-user": 4,
        "thief": 4,
        "elf": 6,
        "dwarf": 8,
        "halfling": 6,
    }

    SAVES = {
        "cleric":     {"poison": 11, "wands": 12, "paralysis": 14, "breath": 16, "spells": 15},
        "dwarf":      {"poison": 10, "wands": 11, "paralysis": 12, "breath": 13, "spells": 14},
        "halfling":   {"poison": 10, "wands": 11, "paralysis": 12, "breath": 13, "spells": 14},
        "elf":        {"poison": 12, "wands": 13, "paralysis": 13, "breath": 15, "spells": 15},
        "fighter":    {"poison": 12, "wands": 13, "paralysis": 14, "breath": 15, "spells": 16},
        "magic-user": {"poison": 13, "wands": 14, "paralysis": 13, "breath": 16, "spells": 15},
        "thief":      {"poison": 13, "wands": 14, "paralysis": 13, "breath": 16, "spells": 15},
    }

    @staticmethod
    def from_json(json_str):
        json_dict = json.loads(json_str)

        new_character = Character()
        new_character.update(json_dict)

        return new_character

    @staticmethod
    def load(file_name):
        full_path = os.path.join(config["data_root"], file_name)

        with open(full_path) as character_file:
            json_str = character_file.read()

        return Character.from_json(json_str)

    def __init__(self):
        self.set_state("new")

    def to_json(self):
        return json.dumps(self, sort_keys=True, indent=4, separators=(',', ': '))

    def save(self, file_name):
        json_str = self.to_json()

        full_path = os.path.join(config["data_root"], file_name)

        with open(full_path, "w") as character_file:
            character_file.write(json_str)

    def roll_stats(self):
        self["strength"] = dice.roll(3, 6)
        self["dexterity"] = dice.roll(3, 6)
        self["constitution"] = dice.roll(3, 6)
        self["intelligence"] = dice.roll(3, 6)
        self["wisdom"] = dice.roll(3, 6)
        self["charisma"] = dice.roll(3, 6)

    def set_class(self, class_name):
        if class_name not in Character.VALID_CLASSES:
            raise ValueError("{} is not a valid character class!".format(class_name))

        self["class"] = class_name

    def roll_equipment(self):
        equipment_roll = dice.roll(3, 6)

        self["equipment"] = equipment.get_equipment(self["class"], equipment_roll)

    def roll_hp(self):
        hp_total = dice.roll(1, Character.HP_DICE[self["class"]]) + self.get_mod("constitution")

        if hp_total < 1:
            hp_total = 1

        self["hit_points"] = hp_total

    def set_name(self, name):
        self["name"] = name

    def set_state(self, state):
        self["state"] = state

    def get_mod_text(self, stat):
        if stat not in self:
            return "+?"

        else:
            value = self.get_mod(stat)
            return ("+{}" if value >= 0 else "{}").format(value)

    def get_mod(self, stat):
        stat = self[stat]

        if stat <= 3:
            return -3
        elif 4 <= stat <= 5:
            return -2
        elif 6 <= stat <= 8:
            return -1
        elif 9 <= stat <= 12:
            return 0
        elif 13 <= stat <= 15:
            return +1
        elif 16 <= stat <= 17:
            return +2
        elif stat >= 18:
            return +3

    def set_saves(self):
        self.update(Character.SAVES[self["class"]])

    def set_thaco(self):
        self["thaco"] = 19

    def get_to_hits(self, start_ac, stop_ac):
        if "thaco" in self:
            thaco = self["thaco"]
        else:
            thaco = 19

        base_to_hits = [thaco - ac for ac in range(start_ac, stop_ac-1, -1)]
        base_to_hits = [_ if _ <= 20 else 20 for _ in base_to_hits]

        return base_to_hits

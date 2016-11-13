import uuid

import character

character_key = str(uuid.uuid4())

new_character = character.Character()
new_character.save(character_key + ".json")

print("The URL for this character is: http://45.55.128.23:5000/{}".format(character_key))

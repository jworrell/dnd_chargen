import json
import os.path

import character as character_module

config = json.load(open(os.environ["CHARGEN_CONFIG"]))

for item in os.listdir(config["data_root"]):
    character = character_module.Character.load(os.path.join(config["data_root"], item))
    print("http://45.55.128.23:5000/{}".format(item.split(".")[0]),
          character["state"],)

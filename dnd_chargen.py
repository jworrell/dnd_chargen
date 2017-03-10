import datetime
import json
import os
import uuid

import flask
import jinja2

import character as character_module

config = json.load(open(os.environ["CHARGEN_CONFIG"]))

dnd_chargen = flask.Blueprint('dnd_chargen', __name__, template_folder='templates')


def load_character(key):
    character = character_module.Character.load(key + ".json")

    return character


def save_character(character, key):
    character.save(key + ".json")


@dnd_chargen.context_processor
def utility_processor():
    def render_stat(stat):
        if isinstance(stat, jinja2.runtime.Undefined):
            return "???"

        return stat

    def render_time(time):
        return datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')

    return {
        "render_stat": render_stat,
        "render_time": render_time,
    }


@dnd_chargen.route('/')
def index():
    return "You must be given a key to use this service!"


@dnd_chargen.route('/<key>')
def hub(key):
    character = load_character(key)

    if character["state"] == "new":
        return flask.redirect(flask.url_for("dnd_chargen.roll_stats", key=key))
    elif character["state"] == "has-stats":
        return flask.redirect(flask.url_for("dnd_chargen.pick_class", key=key))
    elif character["state"] == "has-class":
        return flask.redirect(flask.url_for("dnd_chargen.roll_hp_and_gear", key=key))

    return flask.render_template("character.html", character=character)


@dnd_chargen.route('/roll_stats/<key>', methods=["GET"])
def roll_stats(key):
    character = load_character(key)

    if character["state"] != "new":
        return flask.redirect(flask.url_for("dnd_chargen.hub", key=key))

    return flask.render_template("roll_stats.html",
                                 character=character,
                                 key=key,
                                 submit_url=flask.url_for("dnd_chargen.roll_stats", key=key))


@dnd_chargen.route('/roll_stats/<key>', methods=["POST"])
def do_roll_stats(key):
    character = load_character(key)

    if character["state"] != "new":
        return flask.redirect(flask.url_for("dnd_chargen.hub", key=key))

    character.roll_stats()
    character.set_state("has-stats")

    save_character(character, key)

    return flask.redirect(flask.url_for("dnd_chargen.hub", key=key))


@dnd_chargen.route('/pick_class/<key>', methods=["GET"])
def pick_class(key):
    character = load_character(key)

    if character["state"] != "has-stats":
        return flask.redirect(flask.url_for("dnd_chargen.hub", key=key))

    return flask.render_template("pick_class.html",
                                 character=character,
                                 key=key,
                                 submit_url=flask.url_for("dnd_chargen.pick_class", key=key))


@dnd_chargen.route('/pick_class/<key>', methods=["POST"])
def do_pick_class(key):
    stat_translation = {
        "str": "strength",
        "dex": "dexterity",
        "con": "constitution",
        "int": "intelligence",
        "wis": "wisdom",
        "chr": "charisma"
    }

    character = load_character(key)

    if character["state"] != "has-stats":
        return flask.redirect(flask.url_for("dnd_chargen.hub", key=key))

    if flask.request.form["left-stat"] in ["str", "dex", "con", "int", "wis", "chr"] \
            and flask.request.form["right-stat"] in ["str", "dex", "con", "int", "wis", "chr"] \
            and flask.request.form["left-stat"] != flask.request.form["right-stat"]:

        left_key = stat_translation[flask.request.form["left-stat"]]
        right_key = stat_translation[flask.request.form["right-stat"]]

        swap = character[left_key]
        character[left_key] = character[right_key]
        character[right_key] = swap

    character.set_class(flask.request.form["character_class"])
    character.set_saves()
    character.set_name(flask.request.form["name"])
    character.set_state("has-class")
    save_character(character, key)

    return flask.redirect(flask.url_for("dnd_chargen.hub", key=key))


@dnd_chargen.route('/roll_hp_and_gear/<key>', methods=["GET"])
def roll_hp_and_gear(key):
    character = load_character(key)

    if character["state"] != "has-class":
        return flask.redirect(flask.url_for("dnd_chargen.hub", key=key))

    return flask.render_template("roll_hp_and_gear.html",
                                 character=character,
                                 key=key,
                                 submit_url=flask.url_for("dnd_chargen.roll_hp_and_gear", key=key))


@dnd_chargen.route('/roll_hp_and_gear/<key>', methods=["POST"])
def do_roll_hp_and_gear(key):
    character = load_character(key)

    if character["state"] != "has-class":
        return flask.redirect(flask.url_for("dnd_chargen.hub", key=key))

    character.roll_hp()
    character.roll_equipment()
    character.set_state("done")

    save_character(character, key)

    return flask.redirect(flask.url_for("dnd_chargen.hub", key=key))


@dnd_chargen.route('/make_character', methods=["GET"])
def make_character():
    return flask.render_template("make_character.html")


@dnd_chargen.route('/make_character', methods=["POST"])
def do_make_character():
    character_key = str(uuid.uuid4())

    new_character = character_module.Character(player_name=flask.request.form["player_name"])
    save_character(new_character, character_key)

    return flask.redirect(flask.url_for("dnd_chargen.hub", key=character_key))


@dnd_chargen.route('/view_characters')
def view_characters():
    characters = []
    links = []

    for item in os.listdir(config["data_root"]):
        character = character_module.Character.load(os.path.join(config["data_root"], item))
        characters.append(character)

        link = flask.url_for("dnd_chargen.hub", key=item.split(".")[0])
        links.append(link)

    items = zip(characters, links)

    return flask.render_template("view_characters.html", items=items)

app = flask.Flask(__name__)
app.register_blueprint(dnd_chargen, url_prefix='/chargen')

if __name__ == '__main__':
    app.run("0.0.0.0")

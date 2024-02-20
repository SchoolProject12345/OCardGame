import os
import shutil
import re


def add_cards(target_dir, card_dir):
    elements = {
        "fire": "fire",
        "water": "wtr",
        "earth": "ert",
        "air": "air",
        "chaos": "cha",
    }

    for element in elements:
        if not os.path.exists(os.path.join(target_dir, element)):
            os.makedirs(os.path.join(target_dir, element.capitalize()))
            print("Created directory: ", os.path.join(
                target_dir, element.capitalize()))

    for card in os.listdir(card_dir):
        card_list = re.split("_|\\.", card)
        match card_list[1]:
            case "fire":
                card_element = "Fire"
            case "wtr":
                card_element = "Water"
            case "ert":
                card_element = "Earth"
            case "air":
                card_element = "Air"
            case "cha":
                card_element = "Chaos"

        card_loc = "_"
        card_loc = card_loc.join(card_list[1:-1])
        print(card_list[1:-1])

        if not os.path.exists(os.path.join(target_dir, card_element, card_loc)):
            os.makedirs(os.path.join(target_dir, card_element, card_loc))
            print(
                "Created directory: ", os.path.join(
                    target_dir, card_element, card_loc)
            )

        card_name = "_"
        card_name = card_name.join(card_list[:-1]) + "." + card_list[-1]

        print(
            shutil.move(
                src=os.path.join(card_dir, card),
                dst=os.path.join(target_dir, card_element,
                                 card_loc, card_name),
            )
        )


add_cards("/Users/etudiant/Documents/OCardGame/ChaosCardGame/Assets/Graphics/Cards",
          "/Users/etudiant/Downloads/OCG Cards")

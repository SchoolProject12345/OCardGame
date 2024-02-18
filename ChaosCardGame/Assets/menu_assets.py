import utility
import pygame
import os
from Debug.DEV_debug import load_cards
from dataclasses import dataclass
import logging


def alpha_converter(objects: list[pygame.Surface] | list[list]):
    for object in objects:
        if type(object) == list:
            alpha_converter(object)
        else:
            object = object.convert_alpha()
    return objects


def smoothscale_converter(objects: list[pygame.Surface] | list[list], factor: float):
    for i, item in enumerate(objects):
        if isinstance(item, list):
            smoothscale_converter(item, factor)
        else:
            objects[i] = pygame.transform.smoothscale_by(item, factor)
    return objects


def transform_button_files(path: str):
    """
    Returns a list containing the surfaces to all elements in a directory.

    """
    o_dir = path
    curated_list = []
    processed_list = []
    for object in os.listdir(o_dir):
        if os.path.isfile(os.path.join(o_dir, object)):
            curated_list.append(os.path.join(o_dir, object))
    for path in curated_list:
        if "_i_" in path:
            index_1 = path
        elif "_h_" in path:
            index_2 = path
        elif "_c_" in path:
            index_3 = path
        elif ".DS" in path:
            pass
        else:
            raise ValueError(f"Not enough states. ({path})")
    curated_list = [index_1, index_2, index_3]
    for path in curated_list:
        processed_list.append(pygame.image.load(path))
    return processed_list


def name_sorter(name_list: list):
    sorted_list = [0, 0, 0]

    for name in name_list:
        if "_i_" in name:
            sorted_list[0] = name
        elif "_h_" in name:
            sorted_list[1] = name
        elif "_c_" in name:
            sorted_list[2] = name
    for name in sorted_list:
        if name == 0:
            name = sorted_list[0]
    return sorted_list


def transform_toggle_files(path: str):
    o_dir = path
    small_toggle = []
    big_toggle = []

    for toggle_type in os.listdir(o_dir):
        if "UnToggled" in toggle_type:
            target_list = small_toggle
        elif "Toggled" in toggle_type:
            target_list = big_toggle
        else:
            continue
        for file in os.listdir(os.path.join(o_dir, toggle_type)):
            target_list.append(os.path.join(o_dir, toggle_type, file))
    small_toggle = name_sorter(small_toggle)
    big_toggle = name_sorter(big_toggle)
    for i in range(len(small_toggle)):
        small_toggle[i] = pygame.image.load(small_toggle[i])
    for i in range(len(big_toggle)):
        big_toggle[i] = pygame.image.load(big_toggle[i])
    return [small_toggle, big_toggle]


def process_card_dir(path, i):
    curated_list = ["placeholder" for _ in range(i)]

    for file in os.listdir(path):
        filepath = os.path.join(path, file)
        if file.startswith("."):
            continue
        elif file.startswith("s_"):
            curated_list[0] = pygame.image.load(filepath)
        else:
            curated_list[1] = pygame.image.load(filepath)
    return curated_list


def process_card_dir_2(path, i: int, prefixes: list):
    curated_list = ["placeholder" for _ in range(i)]
    for file in os.listdir(path):
        filepath = os.path.join(path, file)
        for prefix in prefixes:
            if file.startswith(prefix):
                curated_list[prefixes.index(prefix)] = pygame.image.load(filepath)    
    return curated_list


def handle_card_assets(directory_path):
    cards_assets = {}
    for dirpath, dirname, filename in os.walk(directory_path):
        if filename:
            cards_assets[os.path.basename(dirpath)] = {
                "path": dirpath,
                "processed_img": process_card_dir_2(dirpath, 2,["s_"]),
            }
    return cards_assets


graphics_path = os.path.join(utility.cwd_path, "Assets", "Graphics", "")


@dataclass
class MenuBackgrounds:
    """
    A class used to represent backgrounds.

    """

    # Background Images
    bg_dir = os.path.join(graphics_path, "Backgrounds", "")

    bg_main_menu_path = bg_dir + "main_menu_empty.png"
    bg_main_menu_image = pygame.image.load(bg_main_menu_path)

    bg_credits_menu_path = bg_dir + "credits_menu_empty.png"
    bg_credits_menu_image = pygame.image.load(bg_credits_menu_path)

    bg_play_menu_path = bg_dir + "play_menu_empty.png"
    bg_play_menu_image = pygame.image.load(bg_play_menu_path)

    bg_cards_menu_path = bg_dir + "cards_menu_empty.png"
    bg_cards_menu_image = pygame.image.load(bg_cards_menu_path)

    bg_game_menu_path = bg_dir + "game_menu_empty.png"
    bg_game_menu_image = pygame.image.load(bg_game_menu_path)

    bg_card_holder_path = bg_dir + "card_holder_empty.png"
    bg_card_holder_image = pygame.image.load(bg_card_holder_path)

    bg_pause_menu_path = bg_dir + "pause_menu_empty.png"
    bg_pause_menu_image = pygame.image.load(bg_pause_menu_path)

    bg_host_menu_path = bg_dir + "host_menu_empty.png"
    bg_host_menu_image = pygame.image.load(bg_host_menu_path)

    bg_host_menu_path = bg_dir + "host_menu_empty.png"
    bg_host_menu_image = pygame.image.load(bg_host_menu_path)

    bg_join_menu_path = bg_dir + "join_menu_empty.png"
    bg_join_menu_image = pygame.image.load(bg_join_menu_path)

    bg_deck_menu_path = bg_dir + "deck_menu_empty.png"
    bg_deck_menu_image = pygame.image.load(bg_deck_menu_path)

    bg_hand_menu_path = bg_dir + "hand_menu_empty.png"
    bg_hand_menu_image = pygame.image.load(bg_hand_menu_path)

    bg_air_lobby_path = bg_dir + "air_lobby_empty.png"
    bg_air_lobby_image = pygame.image.load(bg_air_lobby_path)

    # Tutorial
    bg_tutorial1_path = bg_dir + "tutorial1_empty.png"
    bg_tutorial1_image = pygame.image.load(bg_tutorial1_path)

    bg_tutorial2_path = bg_dir + "tutorial2_empty.png"
    bg_tutorial2_image = pygame.image.load(bg_tutorial2_path)

    bg_tutorial3_path = bg_dir + "tutorial3_empty.png"
    bg_tutorial3_image = pygame.image.load(bg_tutorial3_path)

    bg_tutorial4_path = bg_dir + "tutorial4_empty.png"
    bg_tutorial4_image = pygame.image.load(bg_tutorial4_path)

    bg_tutorial5_path = bg_dir + "tutorial5_empty.png"
    bg_tutorial5_image = pygame.image.load(bg_tutorial5_path)

    bg_tutorial6_path = bg_dir + "tutorial6_empty.png"
    bg_tutorial6_image = pygame.image.load(bg_tutorial6_path)

    bg_tutorial7_path = bg_dir + "tutorial7_empty.png"
    bg_tutorial7_image = pygame.image.load(bg_tutorial7_path)

    bg_tutorial8_path = bg_dir + "tutorial8_empty.png"
    bg_tutorial8_image = pygame.image.load(bg_tutorial8_path)

    bg_tutorial9_path = bg_dir + "tutorial9_empty.png"
    bg_tutorial9_image = pygame.image.load(bg_tutorial9_path)

    # Lore
    bg_lore1_path = bg_dir + "lore_1_empty.png"
    bg_lore1_image = pygame.image.load(bg_lore1_path)

    bg_lore2_path = bg_dir + "lore_2_empty.png"
    bg_lore2_image = pygame.image.load(bg_lore2_path)

    bg_lore3_path = bg_dir + "lore_3_empty.png"
    bg_lore3_image = pygame.image.load(bg_lore3_path)

    bg_lore4_path = bg_dir + "lore_4_empty.png"
    bg_lore4_image = pygame.image.load(bg_lore4_path)

    bg_lore5_path = bg_dir + "lore_5_empty.png"
    bg_lore5_image = pygame.image.load(bg_lore5_path)

    bg_lore6_path = bg_dir + "lore_6_empty.png"
    bg_lore6_image = pygame.image.load(bg_lore6_path)

    bg_lore7_path = bg_dir + "lore_7_empty.png"
    bg_lore7_image = pygame.image.load(bg_lore7_path)

    bg_lore8_path = bg_dir + "lore_8_empty.png"
    bg_lore8_image = pygame.image.load(bg_lore8_path)

    bg_lore9_path = bg_dir + "lore_9_empty.png"
    bg_lore9_image = pygame.image.load(bg_lore9_path)

    bg_lore10_path = bg_dir + "lore_10_empty.png"
    bg_lore10_image = pygame.image.load(bg_lore10_path)

    bg_lore11_path = bg_dir + "lore_11_empty.png"
    bg_lore11_image = pygame.image.load(bg_lore11_path)

    bg_lore12_path = bg_dir + "lore_12_empty.png"
    bg_lore12_image = pygame.image.load(bg_lore12_path)

    logging.info("Successfully loaded backgrounds")


@dataclass
class MenuButtons:
    """
    A class used to represent buttons used in menus

    """

    button_dir = os.path.join(graphics_path, "Buttons", "")

    # Play
    play_button_path = button_dir + "Play"
    play_button_image = transform_button_files(play_button_path)

    # Cards
    cards_button_path = button_dir + "Cards"
    cards_button_image = transform_button_files(cards_button_path)

    # Credits
    credits_button_path = button_dir + "Credits"
    credits_button_image = transform_button_files(credits_button_path)

    # Join
    join_button_path = button_dir + "Join"
    join_button_image = transform_button_files(join_button_path)

    # Host
    host_button_path = button_dir + "Host"
    host_button_image = transform_button_files(host_button_path)

    # Exit arrow
    exit_arrow_button_path = button_dir + "ExitArrow"
    exit_arrow_button_image = transform_button_files(exit_arrow_button_path)

    # Exit
    exit_button_path = button_dir + "Exit"
    exit_button_image = transform_button_files(exit_button_path)

    # Back
    back_button_path = button_dir + "Back"
    back_button_image = transform_button_files(back_button_path)

    # Settings
    settings_button_path = button_dir + "Settings"
    settings_button_image = transform_button_files(settings_button_path)

    # Surrender
    surrender_button_path = button_dir + "Surrender"
    surrender_button_image = transform_button_files(surrender_button_path)

    # Hand
    hand_button_path = button_dir + "Hand"
    hand_button_image = transform_button_files(hand_button_path)

    # Deck
    deck_button_path = button_dir + "Deck"
    deck_button_image = transform_button_files(deck_button_path)

    # Place
    place_button_path = button_dir + "Place"
    place_button_image = transform_button_files(place_button_path)

    # End Tutorial
    endtutorial_button_path = button_dir + "EndTutorial"
    endtutorial_button_image = transform_button_files(endtutorial_button_path)

    # Next Tutorial
    nexttutorial_button_path = button_dir + "NextTutorial"
    nexttutorial_button_image = transform_button_files(nexttutorial_button_path)

    # Skip Tutorial
    skiptutorial_button_path = button_dir + "SkipTutorial"
    skiptutorial_button_image = transform_button_files(skiptutorial_button_path)

    # Start Tutorial
    starttutorial_button_path = button_dir + "StartTutorial"
    starttutorial_button_image = transform_button_files(starttutorial_button_path)

    # View Lore
    viewlore_button_path = button_dir + "ViewLore"
    viewlore_button_image = transform_button_files(viewlore_button_path)

    logging.info("Successfully loaded buttons")


@dataclass
class CardsMenuToggles:
    """
    A class to represent all toggles in the game.
    """

    toggle_dir = os.path.join(graphics_path, "Toggles", "")

    # Air
    air_toggle_path = toggle_dir + "AirToggle"
    air_toggle_image = transform_toggle_files(air_toggle_path)

    # Chaos
    chaos_toggle_path = toggle_dir + "ChaosToggle"
    chaos_toggle_image = transform_toggle_files(chaos_toggle_path)

    # Earth
    earth_toggle_path = toggle_dir + "EarthToggle"
    earth_toggle_image = transform_toggle_files(earth_toggle_path)

    # Fire
    fire_toggle_path = toggle_dir + "FireToggle"
    fire_toggle_image = transform_toggle_files(fire_toggle_path)

    # Water
    water_toggle_path = toggle_dir + "WaterToggle"
    water_toggle_image = transform_toggle_files(water_toggle_path)

    logging.info("Successfully loaded card menu toggles")


@dataclass
class TextBoxes:
    textbox_dir = os.path.join(graphics_path, "TextBoxes", "")

    # TextBox 1
    textbox_1_path = textbox_dir + "textbox_1.png"
    textbox_1_image = pygame.image.load(textbox_1_path)

    logging.info("Successfully loaded textboxes")


class CardAssets:
    """
    A dataclass to handle and store card assets. The `card_sprites` attribute
    contains processed images of cards, structured by their folder names within
    the Cards directory. Each key represents a folder name, and its value is a dictionary
    with the path to the folder and the processed images ready for game use.
    """

    if load_cards:
        card_sprites = handle_card_assets(os.path.join(graphics_path, "Cards"))

    else:
        card_sprites = handle_card_assets(
            os.path.join(utility.cwd_path, "Debug", "debug_cards")
        )
        logging.warning("Enabled debug cards")
    logging.info("Successfully loaded cards")

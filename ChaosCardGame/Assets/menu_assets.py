import utility
import pygame
import os
from Debug.DEV_debug import load_cards
from dataclasses import dataclass
import logging


def alpha_converter(objects: list[pygame.Surface] | list[list]):
    """
    Recursively converts the images in the list to use alpha channel for transparency.

    Args:
        objects (list[pygame.Surface] | list[list]): The list of Pygame surface objects or nested lists of surface objects to be converted.

    Returns:
        list[pygame.Surface] | list[list]: The list of objects with their alpha channel converted for transparency.
    """
    for object in objects:
        if type(object) == list:
            alpha_converter(object)
        else:
            object = object.convert_alpha()
    return objects


def smoothscale_converter(objects: list[pygame.Surface] | list[list], factor: float):
    """
    Recursively scales the surfaces in the given list of objects by the specified factor using pygame's smoothscale function.

    Args:
        objects (list[pygame.Surface] | list[list]): The list of surfaces or nested lists of surfaces to be scaled.
        factor (float): The scaling factor to be applied to the surfaces.

    Returns:
        list[pygame.Surface] | list[list]: The modified list of scaled surfaces.
    """
    for i, item in enumerate(objects):
        if isinstance(item, list):
            smoothscale_converter(item, factor)
        else:
            objects[i] = pygame.transform.smoothscale_by(item, factor)
    return objects


def dir_sorter(dir_path: str, prefixes):
    if len(prefixes) > len(os.listdir(dir_path)):
        raise ValueError(
            f"{dir_path} and {prefixes} must be of the dame length.")
    sorted_file_path = ["" for _ in range(len(os.listdir(dir_path)))]
    for file in os.listdir(dir_path):
        filepath = os.path.join(dir_path, file)
        for prefix in prefixes:
            if file.startswith(prefix):
                sorted_file_path[prefixes.index(prefix)] = filepath
    sorted_file_path = [item for item in sorted_file_path if item != ""]
    return sorted_file_path


def dict_packager(dir_path_list: list, prefixes: list):
    packaged_dict = {}
    if os.path.isfile(dir_path_list[0]):
        for file_path in dir_path_list:
            packaged_dict[os.path.basename(file_path).split(".")[0]] = {
                "path": file_path,
                "img": pygame.image.load(file_path)
            }
    elif os.path.isdir(dir_path_list[0]):
        for dir_path in dir_path_list:
            if len(prefixes) > 0:
                packaged_dict[os.path.basename(dir_path).split(".")[0]] = {
                    "path": dir_path,
                    "img": [pygame.image.load(os.path.join(dir_path, image)) for image in dir_sorter(dir_path, prefixes)]
                }
            else:
                packaged_dict[os.path.basename(dir_path).split(".")[0]] = {
                    "path": dir_path,
                    "img": [pygame.image.load(os.path.join(dir_path, image)) for image in os.listdir(dir_path) if os.path.basename(image)[0] != "."]
                }
    return packaged_dict


def handle_assets(path: str, per_file=False, prefixes: list = []):
    asset_queue = []
    for dirpath, dirname, filename in os.walk(path):
        if len(dirname) == 0:
            if per_file:
                for file in filename:
                    asset_queue.append(os.path.join(dirpath, file))
            else:
                asset_queue.append(dirpath)
    asset_queue = [
        asset for asset in asset_queue if os.path.basename(asset)[0] != "."]
    return dict_packager(asset_queue, prefixes)


graphics_path = os.path.join(utility.cwd_path, "Assets", "Graphics", "")


@dataclass
class MenuBackgrounds:
    """
    A class used to represent backgrounds.

    """

    # Background Images
    bg_dir = os.path.join(graphics_path, "Backgrounds", "")
    bg_assets = handle_assets(bg_dir, True)
    logging.info("Successfully loaded backgrounds")

    # Lobby
    bg_air_lobby_path = bg_dir + "air_lobby_empty.png"
    bg_air_lobby_image = pygame.image.load(bg_air_lobby_path)

    bg_ert_lobby_path = bg_dir + "ert_lobby_empty.png"
    bg_ert_lobby_image = pygame.image.load(bg_ert_lobby_path)

    bg_fire_lobby_path = bg_dir + "fire_lobby_empty.png"
    bg_fire_lobby_image = pygame.image.load(bg_fire_lobby_path)

    bg_wtr_lobby_path = bg_dir + "wtr_lobby_empty.png"
    bg_wtr_lobby_image = pygame.image.load(bg_wtr_lobby_path)

    bg_cha_lobby_path = bg_dir + "cha_lobby_empty.png"
    bg_cha_lobby_image = pygame.image.load(bg_cha_lobby_path)

    bg_lobby_images = [bg_air_lobby_image, bg_ert_lobby_image,
                       bg_wtr_lobby_image, bg_fire_lobby_image, bg_cha_lobby_image]


@dataclass
class MenuButtons:
    """
    A class used to represent buttons used in menus

    """

    button_dir = os.path.join(graphics_path, "Buttons", "")
    button_assets = handle_assets(button_dir, prefixes=["_i_", "_h_", "_c_"])
    logging.info("Successfully loaded buttons")


@dataclass
class MenuToggles:
    """
    A class to represent all toggles in the game.
    """

    toggle_dir = os.path.join(graphics_path, "Toggles", "")
    toggle_assets = handle_assets(
        toggle_dir, prefixes=["_i2_", "_h2_", "_c2_", "_i1_", "_h1_", "_c1_"]
    )
    logging.info("Successfully loaded card menu toggles")


@dataclass
class TextBoxes:
    """
    A class to represent all textboxes in the game.
    """

    textbox_dir = os.path.join(graphics_path, "TextBoxes", "")
    # TextBox 1
    textbox_1_path = textbox_dir + "textbox_1.png"
    textbox_1_image = pygame.image.load(textbox_1_path)
    logging.info("Successfully loaded textboxes")


@dataclass
class CardAssets:
    """
    A dataclass to handle and store card assets. The `card_sprites` attribute
    contains processed images of cards, structured by their folder names within
    the Cards directory. Each key represents a folder name, and its value is a dictionary
    with the path to the folder and the processed images ready for game use.
    """

    if load_cards:
        card_sprites = handle_assets(
            os.path.join(graphics_path, "Cards"), prefixes=["s_", "b_"]
        )
    else:
        card_sprites = handle_assets(
            os.path.join(utility.cwd_path, "Debug",
                         "debug_card"), prefixes=["s_", "b_"]
        )
        card_sprites.update(
            handle_assets(
                os.path.join(graphics_path, "Cards",
                             "Misc"), prefixes=["s_", "b_"]
            )
        )
        logging.warning("Enabled debug cards")
    logging.info("Successfully loaded cards")


@dataclass
class Fonts:
    pygame.font.init()
    ger_font_path = os.path.join(
        utility.cwd_path, "Assets", "Fonts", "GermaniaOne-Regular.ttf")

    def ger_font(size):
        return pygame.font.Font(Fonts.ger_font_path, size)


@dataclass
class States:
    states_assets = handle_assets(
        os.path.join(graphics_path, "Sprites", "States"),
        True)

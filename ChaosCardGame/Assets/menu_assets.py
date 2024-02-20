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


def process_dir(path, prefixes: list):
    """
    Process the files in the given directory and load images based on the specified prefixes.

    Args:
        path (str): The path of the directory to process.
        prefixes (list): A list of prefixes to filter the files.

    Returns:
        list: A curated list of loaded images based on the prefixes.
    """
    curated_list = ["placeholder" for _ in range(len(prefixes))]
    for file in os.listdir(path):
        filepath = os.path.join(path, file)
        for prefix in prefixes:
            if file.startswith(prefix):
                curated_list[prefixes.index(
                    prefix)] = pygame.image.load(filepath)
            elif prefix == "any":
                curated_list[prefixes.index(
                    prefix)] = pygame.image.load(filepath)

    return curated_list


def handle_assets(
    directory_path: str, size: int, prefixes: list, per_file: bool = False
):
    """
    Handle the assets in the specified directory.

    Args:
        directory_path (str): The path to the directory containing the assets.
        size (int): The size of the assets.
        prefixes (list): The list of prefixes to be applied to the assets.
        per_file (bool, optional): Flag indicating whether to process assets per file or per directory.
            Defaults to False.

    Returns:
        dict: A dictionary containing the processed assets.
    """
    assets = {}
    for dirpath, _, filename in os.walk(directory_path):
        if per_file:
            for file in filename:
                if file[0] == ".":
                    continue
                key = file.split(".")[0]
                assets[key] = {
                    "path": dirpath,
                    "processed_img": pygame.image.load(os.path.join(dirpath, file)),
                }
        else:
            key = os.path.basename(dirpath)
            assets[key] = {
                "path": dirpath,
                "processed_img": process_dir(dirpath, prefixes),
            }
    return assets


graphics_path = os.path.join(utility.cwd_path, "Assets", "Graphics", "")


@dataclass
class MenuBackgrounds:
    """
    A class used to represent backgrounds.

    """

    # Background Images
    bg_dir = os.path.join(graphics_path, "Backgrounds", "")
    bg_assets = handle_assets(bg_dir, 1, ["any"], True)
    logging.info("Successfully loaded backgrounds")


@dataclass
class MenuButtons:
    """
    A class used to represent buttons used in menus

    """

    button_dir = os.path.join(graphics_path, "Buttons", "")
    button_assets = handle_assets(button_dir, 3, ["_i_", "_h_", "_c_"])
    logging.info("Successfully loaded buttons")


@dataclass
class CardsMenuToggles:
    """
    A class to represent all toggles in the game.
    """

    toggle_dir = os.path.join(graphics_path, "Toggles", "")
    toggle_assets = handle_assets(
        toggle_dir, 2, ["_i2_", "_h2_", "_c2_", "_i1_", "_h1_", "_c1_"]
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
            os.path.join(graphics_path, "Cards"), 2, ["s_", "b_"]
        )

    else:
        card_sprites = handle_assets(
            os.path.join(utility.cwd_path, "Debug",
                         "debug_cards"), 2, ["s_", "b_"]
        )
        card_sprites.update(
            handle_assets(
                os.path.join(graphics_path, "Cards",
                             "Misc"), 2, ["s_", "b_"]
            )
        )
        print(card_sprites)
        logging.warning("Enabled debug cards")
    logging.info("Successfully loaded cards")

import pygame
import os
from dataclasses import dataclass


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


@dataclass
class MenuBackgrounds:
    """
    A class used to represent backgrounds.

    """

    # Background Images
    bg_dir = os.path.join("Assets", "Graphics", "Backgrounds", "")

    bg_main_menu_path = bg_dir + "main_menu_empty.png"
    bg_main_menu_image = pygame.image.load(bg_main_menu_path)

    bg_credits_menu_path = bg_dir + "credits_menu_empty.png"
    bg_credits_menu_image = pygame.image.load(bg_credits_menu_path)

    bg_play_menu_path = bg_dir + "play_menu_empty.png"
    bg_play_menu_image = pygame.image.load(bg_play_menu_path)

    bg_cards_menu_path = bg_dir + "cards_menu_empty.png"
    bg_cards_menu_image = pygame.image.load(bg_cards_menu_path)


@dataclass
class MenuButtons:
    """
    A class used to represent buttons used in menus

    """

    button_dir = os.path.join("Assets", "Graphics", "Buttons", "")

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


@dataclass
class CardsMenuToggles:
    """
    A class to represent all toggles in the game.
    """
    toggle_dir = os.path.join("Assets", "Graphics", "Toggles", "")

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

@dataclass
class Cards:
    """
    A class to represent all air cards in the game.
    """
    air_cards_dir = os.path.join("Assets", "Graphics", "Cards", "Air", "")
    chaos_cards_dir = os.path.join("Assets", "Graphics", "Cards", "Chaos", "")
    earth_cards_dir = os.path.join("Assets", "Graphics", "Cards", "Earth", "")
    fire_cards_dir = os.path.join("Assets", "Graphics", "Cards", "Fire", "")
    water_cards_dir = os.path.join("Assets", "Graphics", "Cards", "Water", "")


## Air
    # Commander
    air_commander_path = air_cards_dir + "Commander"
    air_commander_image = transform_toggle_files(air_commander_path)

    # Crystal Bat
    crystalbat_path = air_cards_dir + "CrystalBat"
    crystalbat_image = transform_toggle_files(crystalbat_path)

    # Mystical Owl
    mysticalowl_path = air_cards_dir + "MysticalOwl"
    mysticalowl_image = transform_toggle_files(mysticalowl_path)

    # Mythical Pegasus
    mythicalpegasus_path = air_cards_dir + "MythicalPegasus"
    mythicalpegasus_image = transform_toggle_files(mythicalpegasus_path)

    # Rio o Colorido
    riocolorido_path = air_cards_dir + "RioColorido"
    riocolorido_image = transform_toggle_files(riocolorido_path)

    # Silver Crow
    silvercrow_path = air_cards_dir + "SilverCrow"
    silvercrow_image = transform_toggle_files(silvercrow_path)

    # Skybound Serpent
    skyboundserpent_path = air_cards_dir + "SkyboundSerpent"
    skyboundserpent_image = transform_toggle_files(skyboundserpent_path)

    # Sky Monkey
    skymonkey_path = air_cards_dir + "SkyMonkey"
    skymonkey_image = transform_toggle_files(skymonkey_path)

    # Whispering Sprite
    whisperingsprite_path = air_cards_dir + "WhisperingSprite"
    whisperingsprite_image = transform_toggle_files(whisperingsprite_path)

## Chaos
    # Commander
    chaos_commander_path = chaos_cards_dir + "Commander"
    chaos_commander_image = transform_toggle_files(chaos_commander_path)

    # Chaos Brigade
    chaosbrigade_path = chaos_cards_dir + "ChaosBrigade"
    chaosbrigade_image = transform_toggle_files(chaosbrigade_path)

    # Chaos Emperor
    chaosemperor_path = chaos_cards_dir + "ChaosEmperor"
    chaosemperor_image = transform_toggle_files(chaosbrigade_path)

    # Consumed Werewolf
    consumedwerewolf_path = chaos_cards_dir + "ConsumedWerewolf"
    consumedwerewolf_image = transform_toggle_files(consumedwerewolf_path)

    # Soulfire Demon
    soulfiredemon_path = chaos_cards_dir + "SoulfireDemon"
    soulfiredemon_image = transform_toggle_files(soulfiredemon_path)

    # Tenebrous Mage
    tenebrousmage_path = chaos_cards_dir + "TenebrousMage"
    tenebrousmage_image = transform_toggle_files(tenebrousmage_path)

    # Tormented Warrior
    tormentedwarrior_path = chaos_cards_dir + "TormentedWarrior"
    tormentedwarrior_image = transform_toggle_files(tormentedwarrior_path)

    # Void Gargoyle
    voidgargoyle_path = chaos_cards_dir + "VoidGargoyle"
    voidgargoyle_image = transform_toggle_files(voidgargoyle_path)

    # Void Ultraray
    voidultraray_path = chaos_cards_dir + "VoidUltraray"
    voidultraray_image = transform_toggle_files(voidultraray_path)

## Earth
    # Commander
    earth_commander_path = earth_cards_dir + "Commander"
    earth_commander_image = transform_toggle_files(earth_commander_path)

    # Blossom Sylph
    blossomsylph_path = earth_cards_dir + "BlossomSylph"
    blossomsylph_image = transform_toggle_files(blossomsylph_path)

    # Bulk Cherry
    bulkcherry_path = earth_cards_dir + "BulkCherry"
    bulkcherry_image = transform_toggle_files(bulkcherry_path)

    #Energy Cat
    energycat_path = earth_cards_dir + "EnergyCat"
    energycat_image = transform_toggle_files(energycat_path)

    # Everstone Symbiote
    everstonesymbiote_path = earth_cards_dir + "EverstoneSymbiote"
    everstonesymbiote_image = transform_toggle_files(everstonesymbiote_path)

    # Fern Goat
    ferngoat_path = earth_cards_dir + "FernGoat"
    ferngoat_image = transform_toggle_files(ferngoat_path)

    # Shokubutsu
    shokubutsu_path = earth_cards_dir + "Shokubutsu"
    shokubutsu_image = transform_toggle_files(shokubutsu_path)

    # Vine Serpent
    vineserpent_path = earth_cards_dir + "VineSerpent"
    vineserpent_image = transform_toggle_files(vineserpent_path)

    # Wise Golem
    wisegolem_path = earth_cards_dir + "WiseGolem"
    wisegolem_image = transform_toggle_files(wisegolem_path)

## Fire
    # Commander
    fire_commander_path = fire_cards_dir + "Commander"
    fire_commander_image = transform_toggle_files(fire_commander_path)
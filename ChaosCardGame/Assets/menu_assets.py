import utility
import pygame
import os
from Debug.DEV_debug import load_cards
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


def transform_card_files(path: str):
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
        processed_path = path.split("/")[-1]
        if processed_path.startswith("s_"):
            index_small = path
        elif processed_path.endswith(".DS"):
            pass
        else:
            index_big = path
    curated_list = [index_small, index_big]
    for path in curated_list:
        processed_list.append(pygame.image.load(path))
    return processed_list


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


if load_cards:
    @dataclass
    class Cards:
        """
        A class to represent all air cards in the game.
        """
        air_cards_dir = os.path.join(graphics_path, "Cards", "air_cards", "")
        chaos_cards_dir = os.path.join(
            graphics_path, "Cards", "chaos_cards", "")
        earth_cards_dir = os.path.join(
            graphics_path, "Cards", "earth_cards", "")
        fire_cards_dir = os.path.join(graphics_path, "Cards", "fire_cards", "")
        water_cards_dir = os.path.join(
            graphics_path, "Cards", "water_cards", "")

    # Air
        # Commander
        air_commander_path = air_cards_dir + "commander"
        air_commander_image = transform_card_files(air_commander_path)

        # Crystal Bat
        crystalbat_path = air_cards_dir + "crystalbat"
        crystalbat_image = transform_card_files(crystalbat_path)

        # Mystical Owl
        mysticalowl_path = air_cards_dir + "mysticalowl"
        mysticalowl_image = transform_card_files(mysticalowl_path)

        # Mythical Pegasus
        mythicalpegasus_path = air_cards_dir + "mythicalpegasus"
        mythicalpegasus_image = transform_card_files(mythicalpegasus_path)

        # Rio o Colorido
        riocolorido_path = air_cards_dir + "riocolorido"
        riocolorido_image = transform_card_files(riocolorido_path)

        # Silver Crow
        silvercrow_path = air_cards_dir + "silvercrow"
        silvercrow_image = transform_card_files(silvercrow_path)

        # Skybound Serpent
        skyboundserpent_path = air_cards_dir + "skyboundserpent"
        skyboundserpent_image = transform_card_files(skyboundserpent_path)

        # Sky Monkey
        skymonkey_path = air_cards_dir + "skymonkey"
        skymonkey_image = transform_card_files(skymonkey_path)

        # Whispering Sprite
        whisperingsprite_path = air_cards_dir + "whisperingsprite"
        whisperingsprite_image = transform_card_files(whisperingsprite_path)

    # Chaos
        # Commander
        chaos_commander_path = chaos_cards_dir + "commander"
        chaos_commander_image = transform_card_files(chaos_commander_path)

        # Chaos Brigade
        chaosbrigade_path = chaos_cards_dir + "chaosbrigade"
        chaosbrigade_image = transform_card_files(chaosbrigade_path)

        # Chaos Emperor
        chaosemperor_path = chaos_cards_dir + "chaosemperor"
        chaosemperor_image = transform_card_files(chaosbrigade_path)

        # Consumed Werewolf
        consumedwerewolf_path = chaos_cards_dir + "consumedwerewolf"
        consumedwerewolf_image = transform_card_files(consumedwerewolf_path)

        # Soulfire Demon
        soulfiredemon_path = chaos_cards_dir + "soulfiredemon"
        soulfiredemon_image = transform_card_files(soulfiredemon_path)

        # Tenebrous Mage
        tenebrousmage_path = chaos_cards_dir + "tenebrousmage"
        tenebrousmage_image = transform_card_files(tenebrousmage_path)

        # Tormented Warrior
        tormentedwarrior_path = chaos_cards_dir + "tormentedwarrior"
        tormentedwarrior_image = transform_card_files(tormentedwarrior_path)

        # Void Gargoyle
        voidgargoyle_path = chaos_cards_dir + "voidgargoyle"
        voidgargoyle_image = transform_card_files(voidgargoyle_path)

        # Void Ultraray
        voidultraray_path = chaos_cards_dir + "voidultraray"
        voidultraray_image = transform_card_files(voidultraray_path)

    # Earth
        # Commander
        earth_commander_path = earth_cards_dir + "commander"
        earth_commander_image = transform_card_files(earth_commander_path)

        # Blossom Sylph
        blossomsylph_path = earth_cards_dir + "blossomsylph"
        blossomsylph_image = transform_card_files(blossomsylph_path)

        # Bulk Cherry
        bulkcherry_path = earth_cards_dir + "bulkcherry"
        bulkcherry_image = transform_card_files(bulkcherry_path)

        # Energy Cat
        energycat_path = earth_cards_dir + "energycat"
        energycat_image = transform_card_files(energycat_path)

        # Everstone Symbiote
        everstonesymbiote_path = earth_cards_dir + "everstonesymbiote"
        everstonesymbiote_image = transform_card_files(everstonesymbiote_path)

        # Fern Goat
        ferngoat_path = earth_cards_dir + "ferngoat"
        ferngoat_image = transform_card_files(ferngoat_path)

        # Shokubutsu
        shokubutsu_path = earth_cards_dir + "shokubutsu"
        shokubutsu_image = transform_card_files(shokubutsu_path)

        # Vine Serpent
        vineserpent_path = earth_cards_dir + "vineserpent"
        vineserpent_image = transform_card_files(vineserpent_path)

        # Wise Golem
        wisegolem_path = earth_cards_dir + "wisegolem"
        wisegolem_image = transform_card_files(wisegolem_path)

    # Fire
        # Commander
        fire_commander_path = fire_cards_dir + "commander"
        fire_commander_image = transform_card_files(fire_commander_path)

        # Ashes Hand
        ashes_hand_path = fire_cards_dir + "asheshand"
        ashes_hand_image = transform_card_files(ashes_hand_path)

        # Everburn Wizard
        everburn_wizard_path = fire_cards_dir + "everburnwizard"
        everburn_wizard_image = transform_card_files(everburn_wizard_path)

        # Felix Fyris
        felix_fyris_path = fire_cards_dir + "felixfyris"
        felix_fyris_image = transform_card_files(felix_fyris_path)

        # Fyyronyr
        fyyronyr_path = fire_cards_dir + "fyyronyr"
        fyyronyr_image = transform_card_files(fyyronyr_path)

        # Kratos
        kratos_path = fire_cards_dir + "kratos"
        kratos_image = transform_card_files(kratos_path)

        # Magma Devil
        magma_devil_path = fire_cards_dir + "magmadevil"
        magma_devil_image = transform_card_files(magma_devil_path)

        # Magma Golem
        magma_golem_path = fire_cards_dir + "magmagolem"
        magma_golem_image = transform_card_files(magma_golem_path)

    # Water
        # Commander
        water_commander_path = water_cards_dir + "commander"
        water_commander_image = transform_card_files(water_commander_path)

        # Bob Blobfish
        bob_blobfish_path = water_cards_dir + "bobblobfish"
        bob_blobfish_image = transform_card_files(bob_blobfish_path)

        # Captain Octopus
        captain_octopus_path = water_cards_dir + "captainoctopus"
        captain_octopus_image = transform_card_files(captain_octopus_path)

        # Eternal Sunseeker
        eternal_sunseeker_path = water_cards_dir + "eternalsunseeker"
        eternal_sunseeker_image = transform_card_files(eternal_sunseeker_path)

        # Lamia
        lamia_path = water_cards_dir + "lamia"
        lamia_image = transform_card_files(lamia_path)

        # Sea Hydra
        sea_hydra_path = water_cards_dir + "seahydra"
        seahydra_image = transform_card_files(sea_hydra_path)

        # Shiao
        shiao_path = water_cards_dir + "shiao"
        shiao_image = transform_card_files(shiao_path)

        # Terror Mermaid
        terror_mermaid_path = water_cards_dir + "terrormermaid"
        terror_mermaid_image = transform_card_files(terror_mermaid_path)

        # Thousand Toothed
        thousand_toothed_path = water_cards_dir + "thousandtoothed"
        thousand_toothed_image = transform_card_files(thousand_toothed_path)

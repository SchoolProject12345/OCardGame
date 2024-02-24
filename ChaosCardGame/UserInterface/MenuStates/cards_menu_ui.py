import pygame
import utility
import os
import Core.core_main as core
from Network.server import HandlerHandler as handle
from UserInterface.ui_settings import SCREEN_WIDTH, SCREEN_HEIGHT
from UserInterface.OcgVision.vision_main import (State, ImageToggle,
    ToggleGridFour, ImageButton, TextBox);
from Assets.menu_assets import (MenuBackgrounds, MenuToggles,
    MenuButtons, CardAssets, Fonts, alpha_converter);

def create_image_triplet(
        img: pygame.Surface,
        /,
        factor1: float = 1.0,
        factor2: float = 0.0,
        factor3: float = 0.0,
    ) -> list[pygame.Surface]:
    if factor2 == 0.0:
        factor2 = factor1 * 1.1
    if factor3 == 0.0:
        factor3 = factor2
    return [
        pygame.transform.scale_by(img, factor1),
        pygame.transform.scale_by(img, factor2),
        pygame.transform.scale_by(img, factor3)
    ]

def load_commander_toggle(menu: "CardsMenu", commander: str) -> ImageToggle:
    commander = CardAssets.commander_sprites[commander]["img"]
    return ImageToggle(
        menu.screen,
        call_back = True,
        factor = 1.0,
        image = (create_image_triplet(commander[0], 1.4, 1.5, 1.6)
                 + create_image_triplet(commander[1], 1.0, 1.1, 1.0)),
        position_type = "center",
        position_type_T = "center",
        # absolute center of screen accounted for "buttons" when toggled
        # use y = 335 for center of mass of both pane instead.
        position = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2),
        position_T = ((SCREEN_WIDTH + 33)//2, SCREEN_HEIGHT//2),
    )

def deck_len_color(deck_len: int):
    default_deck_size = core.Constants.default_deck_size
    if deck_len == default_deck_size:
        return  (50, 240, 50)
    if deck_len < default_deck_size:
        return (240, 50 + 190 * deck_len/(default_deck_size - 1), 50)
    return (240, 50, 50)

class CardCollection:
    placeholder = [
        pygame.image.load(os.path.join(
            utility.cwd_path,
            "Assets/Graphics/Cards/Misc/card_not_found/s_card_not_found.png"
        ))] * 3 + [pygame.image.load(os.path.join(
            utility.cwd_path,
            "Assets/Graphics/Cards/Misc/card_not_found/b_card_not_found.png"
        ))] * 3,
        # in case Collection is not big enough
        # (shouldn't happen normally, but better than a throw)

    def __init__(self, screen, element: str):
        self.screen = screen
        self.card_ids: list[str] = []
        self.total = [
            self.generate_toggle_list(dirpath, filenames)
            for (dirpath, _, filenames) in os.walk(os.path.join(utility.cwd_path, f"Assets/Graphics/Cards/{element.strip().title()}"))
            if len(filenames) > 1
        ] # simply read all card assets & display them, no hardcoding
        # 4 + 4 = 8
        if len(self.total) < 8:
            self.total += [self.placeholder] * (8 - len(self.total))
        self.left_side = ToggleGridFour(
            self.screen,
            self.total,
            475, 525,
            (50, 145),
            1.6, 0.8,  # small big cards so they don't overlap too much
        )
        self.right_side = ToggleGridFour(
            self.screen,
            self.total,
            475, 450,
            (SCREEN_WIDTH-475-10, 145),
            1.6, 0.8,  # if they overlap, it would be difficult to create a deck.
            start=4
        )

    def render(self):
        self.left_side.render()
        self.right_side.render()

    def generate_toggle_list(self, dirpath: str, filenames: tuple[str, str]) -> list[pygame.Surface]:
        self.card_ids.append(filenames[0][2:-4]) # remove leading "s_"/"b_" & trailing ".png"
        return create_image_triplet(
                pygame.image.load(
                    os.path.join(utility.cwd_path, dirpath, filenames[1])
                ),
                factor3=1.2,
            ) + create_image_triplet(
                pygame.image.load(
                    os.path.join(utility.cwd_path, dirpath, filenames[0])
                ),
                factor3=1.0,
            )

    def get_toggled(self) -> list[str]:
        "Return all of self's toggled cards to save them in a deck."
        toggles = self.left_side.toggles + self.right_side.toggles
        return [
            # create deck from file name
            self.card_ids[i] for i in range(min(len(self.card_ids), 8))
            if toggles[i].is_toggled
        ]

class CardsMenu(State):
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.is_anchor = False
        self.local_options = ["CardsMenu"]
        super().__init__(self.screen, self.is_anchor, self.local_options)
        self.bg_cards_menu_image = MenuBackgrounds.bg_assets["cards_menu_empty"]["img"].convert_alpha(
        )
        self.bg_cards_menu_rect = self.bg_cards_menu_image.get_rect()

        self.exit_button = ImageButton(
            self.screen,
            True,
            image=alpha_converter(
                MenuButtons.button_assets["ExitArrow"]["img"]),
            position_type="topleft",
            position=(25, 25)
        )

        # Toggle Grids
        padding = 25
        object_width = MenuToggles.toggle_assets["AirToggle"]["img"][0].get_width()
        number_of_toggles = 5
        total_width = SCREEN_WIDTH - 2 * padding - object_width * number_of_toggles
        gap_width = total_width / (number_of_toggles-1)
        toggle_xpos = [padding + object_width/2 +
                       (gap_width + object_width) * i for i in range(number_of_toggles)]
        # Toggles
        self.element_toggles = [
            ImageToggle(
                self.screen, "AirToggle", image=alpha_converter(MenuToggles.toggle_assets["AirToggle"]["img"]), position=(toggle_xpos[0], SCREEN_HEIGHT-20), position_type="midbottom"),
            ImageToggle(
                self.screen, "ChaosToggle", image=alpha_converter(MenuToggles.toggle_assets["ChaosToggle"]["img"]), position=(toggle_xpos[1], SCREEN_HEIGHT-20), position_type="midbottom"),
            ImageToggle(
                self.screen, "EarthToggle", is_toggled=True, image=alpha_converter(MenuToggles.toggle_assets["EarthToggle"]["img"]), position=(toggle_xpos[2], SCREEN_HEIGHT-20), position_type="midbottom"),
            ImageToggle(
                self.screen, "WaterToggle", image=alpha_converter(MenuToggles.toggle_assets["WaterToggle"]["img"]), position=(toggle_xpos[3], SCREEN_HEIGHT-20), position_type="midbottom"),
            ImageToggle(
                self.screen, "FireToggle", image=alpha_converter(MenuToggles.toggle_assets["FireToggle"]["img"]), position=(toggle_xpos[4], SCREEN_HEIGHT-20), position_type="midbottom")
        ]
        self.active_toggle = 2
        self.new_toggle = None

        # Init all cards and grids here
        # Tuple so immutable hence less memory
        self.grids: tuple[CardCollection, ...] = (
            CardCollection(self.screen, "air"),
            CardCollection(self.screen, "chaos"),
            CardCollection(self.screen, "earth"),
            CardCollection(self.screen, "water"),
            CardCollection(self.screen, "fire"),
        )
        # Commanders
        self.commanders: tuple[ImageToggle, ...] = (
            load_commander_toggle(self, "air_skyvisindi"),
            load_commander_toggle(self, "cha_vafisorg"),
            load_commander_toggle(self, "ert_valkejord"),
            load_commander_toggle(self, "wtr_krakithrek"),
            load_commander_toggle(self, "fire_aevilogi"),
        )
        self.commander_names: tuple[str, ...] = (
            "skyvisindi",
            "vafisorg",
            "valkejord",
            "krakithrek",
            "aevilogi",
        )
        # Deck size (for information)
        self.deck_len_text = TextBox(
            screen,
            (SCREEN_WIDTH//2, 160),
            100,
            50,
            Fonts.ger_font(25),
            (240, 50, 50),
            "center",
            "center",
            text=f"Cards selected: 0/{core.Constants.default_deck_size}"
        )

    def untoggle_commanders(self):
        "Untoggle every commanders but the active one."
        for i in range(5):
            if i == self.active_toggle:
                continue
            self.commanders[i].is_toggled = False
    
    def get_toggled_commander(self) -> str:
        for i, commander in enumerate(self.commander_names):
            if self.commanders[i].is_toggled:
                return commander
        return "commander_not_found"

    def save_deck(self) -> None:
        deck: list[str] = []
        for grid in self.grids:
            deck.extend(grid.get_toggled())
        #if len(deck) != core.Constants.default_deck_size:
        #    #= TODO: make popup warning or something =#
        # save anyway because the server might have different rules.
        handle.deck = deck # save deck to handle and wait for username to save in `players.txt`
        handle.commander = self.get_toggled_commander()

    def get_deck_length(self) -> int:
        count: int = 0
        for grid in self.grids:
            count += len(grid.get_toggled())
        return count

    def cards_menu(self):
        self.screen.blit(self.bg_cards_menu_image, self.bg_cards_menu_rect)
        self.exit_button.render()
        if self.exit_button.answer() or pygame.key.get_pressed()[pygame.K_ESCAPE]:
            self.save_deck()
            self.revert_state(1)
        # Toggle selector
        for index, toggle in enumerate(self.element_toggles):
            if toggle.is_toggled:
                if index != self.active_toggle:
                    self.new_toggle = index
                else:
                    continue
            else:
                toggle.is_toggled = False
        if self.new_toggle != None:
            self.element_toggles[self.active_toggle].is_toggled = False
            self.active_toggle = self.new_toggle
            self.new_toggle = None
        for toggle in self.element_toggles:
            toggle.render()
            toggle.answer()
        # Cards
        self.grids[self.active_toggle].render()
        self.commanders[self.active_toggle].render()
        # can't set `call_back` as `self.untoggle_commanders` for it is a method
        if self.commanders[self.active_toggle].answer():
            self.untoggle_commanders()
        # Text
        deck_len = self.get_deck_length()
        self.deck_len_text.text = f"Cards selected: {deck_len}/{core.Constants.default_deck_size}"
        self.deck_len_text.color = deck_len_color(deck_len)
        self.deck_len_text.render()

    def state_manager_hook(self, app):
        if State.state_tree[1] == self.local_options[0]:
            self.cards_menu()

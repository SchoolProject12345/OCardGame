import pygame
from utility import cwd_path
import os
from Assets.menu_assets import CardAssets
from UserInterface.OcgVision.vision_io import KeyRel
from UserInterface.OcgVision.vision_coordadapter import rect_grid
from UserInterface.OcgVision.vision_main import (
    State,
    ImageButton,
    DualBarVerti,
    TextBox,
)
from UserInterface.event_library import fetch_event
from utility import search_event
from UserInterface.card_handler import CardManager
from Assets.menu_assets import MenuBackgrounds, MenuButtons, alpha_converter
from UserInterface.ui_settings import SCREEN_CENTER, SCREEN_HEIGHT, SCREEN_WIDTH


class GameMenu(State):
    def __init__(self, screen):
        self.game_state = {
            "arena": 2,
            "isactive": True,
            "local": {
                "board": [
                    {
                        "element": 2,
                        "hp": 40,
                        "max_hp": 40,
                        "name": "debug_card",
                        "state": "default",
                    },
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                ],
                "commander": {
                    "charges": 0,
                    "element": 3,
                    "hp": 600,
                    "max_hp": 600,
                    "name": "air_skyvisindi",
                    "state": "default",
                },
                "deck_length": 10,
                "discard": [],
                "energy": 2,
                "energy_per_turn": 3,
                "hand": [
                    "wtr_bobtheblobfish",
                    "wtr_mermaidofterror",
                    "fire_magmagolem",
                    "air_tornadospell",
                ],
                "max_energy": 5,
                "name": "Ånyks",
            },
            "remote": {
                "board": [None, None, None, None, None, None, None],
                "commander": {
                    "charges": 0,
                    "element": 1,
                    "hp": 600,
                    "max_hp": 600,
                    "name": "debug_card",
                    "state": "default",
                },
                "deck_length": 10,
                "discard": [],
                "energy": 4,
                "energy_per_turn": 3,
                "hand": [
                    "cha_voidultraray",
                    "air_mysticalowl",
                    "ert_vineserpent",
                    "cha_tenebrousmage",
                    "ert_everstonesymbiote",
                ],
                "max_energy": 4,
                "name": "Dev",
            },
            "roomname": "",
            "turn": 0,
        }

        self.screen = screen
        self.is_anchor = False
        self.local_options = ["GameMenu"]
        super().__init__(self.screen, self.is_anchor, self.local_options)
        self.escp_rel = KeyRel(pygame.K_ESCAPE)
        self.ui_state = {
            "paused": False,
            "decked": False,
            "handed": False,
            "popped": False,
        }
        self.ger_font_path = os.path.join(
            cwd_path, "Assets", "Fonts", "GermaniaOne-Regular.ttf"
        )
        self.player_max_energy = 5
        self.player_health = 500
        self.player_energy = 4
        self.enemy_max_energy = 5
        self.enemy_health = 250
        self.enemy_energy = 2

        # Game Menu
        self.bg_game_menu_image = MenuBackgrounds.bg_assets["earth_arena"][
            "img"
        ].convert_alpha()
        self.bg_game_menu_rect = self.bg_game_menu_image.get_rect(
            topleft=(0, 0))

        # Buttons
        self.hand_button = ImageButton(
            self.screen,
            True,
            image=alpha_converter(MenuButtons.button_assets["Hand"]["img"]),
            position_type="topleft",
            position=(296, 706),
        )

        self.deck_button = ImageButton(
            self.screen,
            True,
            image=alpha_converter(MenuButtons.button_assets["Deck"]["img"]),
            position_type="topleft",
            position=(824, 706),
        )

        # Bars
        self.player_health_bar = DualBarVerti(
            self.screen,
            position=(566, 706),
            position_type="topleft",
            width=96,
            height=52,
            color_bg=pygame.color.Color(220, 220, 220),
            color_fg=pygame.color.Color(255, 122, 122),
            max_value=600,
        )

        self.player_energy_bar = DualBarVerti(
            self.screen,
            position=(683, 706),
            position_type="topleft",
            width=96,
            height=52,
            color_bg=pygame.color.Color(220, 220, 220),
            color_fg=pygame.color.Color(122, 215, 255),
            max_value=self.player_max_energy,
        )

        self.enemy_health_bar = DualBarVerti(
            self.screen,
            position=(566, 0),
            position_type="topleft",
            width=96,
            height=52,
            color_bg=pygame.color.Color(220, 220, 220),
            color_fg=pygame.color.Color(255, 122, 122),
            max_value=600,
        )

        self.enemy_energy_bar = DualBarVerti(
            self.screen,
            position=(683, 0),
            position_type="topleft",
            width=96,
            height=52,
            color_bg=pygame.color.Color(220, 220, 220),
            color_fg=pygame.color.Color(122, 215, 255),
            max_value=self.enemy_max_energy,
        )

        # Text Boxes
        self.player_health_bar_text = TextBox(
            self.screen,
            position=(566, 706),
            width=96,
            height=52,
            font=pygame.font.Font(self.ger_font_path, 30),
            color=(101, 101, 101),
            position_type="topleft",
            text_center="center",
            text="",
        )

        self.player_energy_bar_text = TextBox(
            self.screen,
            position=(683, 706),
            width=96,
            height=52,
            font=pygame.font.Font(self.ger_font_path, 30),
            color=(101, 101, 101),
            position_type="topleft",
            text_center="center",
            text="",
        )

        self.enemy_health_bar_text = TextBox(
            self.screen,
            position=(566, 0),
            width=96,
            height=52,
            font=pygame.font.Font(self.ger_font_path, 30),
            color=(101, 101, 101),
            position_type="topleft",
            text_center="center",
            text="",
        )

        self.enemy_energy_bar_text = TextBox(
            self.screen,
            position=(683, 0),
            width=96,
            height=52,
            font=pygame.font.Font(self.ger_font_path, 30),
            color=(101, 101, 101),
            position_type="topleft",
            text_center="center",
            text="",
        )

        self.player_username_text = TextBox(
            self.screen,
            position=(72, 726),
            width=96,
            height=52,
            font=pygame.font.Font(self.ger_font_path, 18),
            color=(255, 255, 255),
            position_type="topleft",
            text_center="center",
            text="",
        )

        # Pause Menu
        self.bg_pause_menu_image = MenuBackgrounds.bg_assets["pause_menu_empty"][
            "img"
        ].convert_alpha()
        self.bg_pause_menu_rect = self.bg_pause_menu_image.get_rect(
            center=SCREEN_CENTER
        )

        # Buttons
        self.pauseback_button = ImageButton(
            self.screen,
            True,
            image=alpha_converter(MenuButtons.button_assets["Back"]["img"]),
            position_type="center",
            position=(SCREEN_CENTER[0], 294),
        )

        self.settings_button = ImageButton(
            self.screen,
            True,
            image=alpha_converter(
                MenuButtons.button_assets["Settings"]["img"]
            ),
            position_type="center",
            position=(SCREEN_CENTER[0], 392),
        )

        self.surrender_button = ImageButton(
            self.screen,
            True,
            image=alpha_converter(
                MenuButtons.button_assets["Surrender"]["img"]
            ),
            postion_type="center",
            position=(SCREEN_CENTER[0], 490),
        )

        # Deck Menu
        self.bg_deck_menu_image = MenuBackgrounds.bg_assets["deck_menu_empty"][
            "img"
        ].convert_alpha()
        self.bg_deck_menu_rect = self.bg_deck_menu_image.get_rect(
            center=SCREEN_CENTER)

        # Buttons
        self.deckback_button = ImageButton(
            self.screen,
            True,
            image=alpha_converter(MenuButtons.button_assets["Back"]["img"]),
            position_type="center",
            position=(SCREEN_CENTER[0], 555),
        )

        # Hand Menu
        self.bg_hand_menu_image = MenuBackgrounds.bg_assets["hand_menu_empty"][
            "img"
        ].convert_alpha()
        self.bg_hand_menu_rect = self.bg_hand_menu_image.get_rect(
            center=SCREEN_CENTER)

        # Buttons
        self.handback_button = ImageButton(
            self.screen,
            True,
            image=alpha_converter(MenuButtons.button_assets["Back"]["img"]),
            position_type="center",
            position=(SCREEN_CENTER[0], 555),
        )
        self.card_manager = CardManager(
            self.screen, len(self.game_state["local"]["board"])
        )

    def handle_events(self, events):
        for event in events:
            if event.type == fetch_event("UI_STATE", raw=True):
                # Access the dictionary attribute using vars()
                event_dict = vars(event)
                for state in event_dict.keys():
                    self.ui_state[state] = event_dict[state]

    # Toggle State
    def is_paused_toggle(self):
        self.ui_state["paused"] = not self.ui_state["paused"]

    def is_decked_toggle(self):
        self.ui_state["decked"] = not self.ui_state["decked"]

    def is_handed_toggle(self):
        self.ui_state["handed"] = not self.ui_state["handed"]

    def game_menu(self):
        # Background elements
        self.screen.blit(self.bg_game_menu_image, self.bg_game_menu_rect)
        self.player_health_bar.render(self.player_health, False)
        self.player_energy_bar.render(self.player_energy, False)
        self.enemy_health_bar.render(self.enemy_health, True)
        self.enemy_energy_bar.render(self.enemy_energy, True)
        self.player_health_bar_text.render(str(self.player_health))
        self.player_energy_bar_text.render(str(self.player_energy))
        self.enemy_health_bar_text.render(str(self.enemy_health))
        self.enemy_energy_bar_text.render(str(self.enemy_energy))

        self.card_manager.render(
            super().events, self.ui_state, self.game_state)

        # User buttons
        self.deck_button.render()
        if self.deck_button.answer():
            self.is_decked_toggle()
        if self.ui_state["decked"]:
            self.screen.blit(self.bg_deck_menu_image, self.bg_deck_menu_rect)
            self.deckback_button.render()
            if self.deckback_button.answer():
                self.is_decked_toggle()
        self.hand_button.render()
        if self.hand_button.answer():
            self.is_handed_toggle()
        if self.ui_state["handed"]:
            self.screen.blit(self.bg_hand_menu_image, self.bg_hand_menu_rect)
            self.handback_button.render()
            if self.handback_button.answer():
                self.is_handed_toggle()

        # Toggles
        if self.escp_rel.update(search_event(super().events, pygame.KEYUP)):
            self.is_paused_toggle()
        if self.ui_state["paused"]:
            self.screen.blit(self.bg_pause_menu_image, self.bg_pause_menu_rect)
            self.pauseback_button.render()
            self.settings_button.render()
            self.surrender_button.render()
            if self.pauseback_button.answer():
                self.is_paused_toggle()
            elif self.settings_button.answer():
                pass
            elif self.surrender_button.answer():
                self.is_paused_toggle()
                self.revert_state(2)

        self.handle_events(super().events)

    def state_manager_hook(self, app):
        if len(State.state_tree) >= 5:
            raise ValueError("Bro what?")
        elif State.state_tree[3] == self.local_options[0]:
            self.game_menu()

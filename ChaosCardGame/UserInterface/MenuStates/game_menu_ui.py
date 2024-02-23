import pygame
import os
import logging
from utility import search_event
from utility import cwd_path
from Network.server import HandlerHandler as handle
from UserInterface.ui_settings import SCREEN_CENTER, SCREEN_HEIGHT, SCREEN_WIDTH
from UserInterface.OcgVision.vision_main import State, ImageButton, DualBar, TextBox
from UserInterface.OcgVision.vision_io import KeyRel
from UserInterface.OcgVision.vision_coordadapter import rect_grid
from UserInterface.event_library import CustomEvents
from UserInterface.card_handler import CardManager
from Assets.menu_assets import MenuBackgrounds, MenuButtons, Fonts, alpha_converter
from Assets.menu_assets import CardAssets


class GameMenu(State):
    def __init__(self, screen):
        self.game_state = {
            "arena": 2,
            "isactive": True,
            "local": {
                "board": [
                    {
                        "element": 2,
                        "hp": 10,
                        "max_hp": 40,
                        "name": "wtr_hydra_of_the_seas",
                        "state": "no_multi",
                    },
                    {
                        "element": 2,
                        "hp": 40,
                        "max_hp": 40,
                        "name": "wtr_eternal_sunseeker",
                        "state": "blocked",
                    },
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
                "board": [None, None, None, {
                    "element": 2,
                    "hp": 20,
                    "max_hp": 40,
                    "name": "air_the_mythical_pegasus",
                    "state": "unattacked",
                }, None, None, None],
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
            "selecting": False
        }
        self.pending_actions = []
        self.player_max_energy = 5
        self.player_health = 500
        self.player_energy = 4
        self.enemy_max_energy = 5
        self.enemy_health = 250
        self.enemy_energy = 2

        # Game Menu
        self.current_arena = self.game_state["arena"]
        self.bg_game_menu_image = MenuBackgrounds.bg_menu_images[
            min(self.current_arena, 4)
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
        self.player_health_bar = DualBar(
            self.screen,
            position=(566, 706),
            position_type="topleft",
            width=96,
            height=52,
            color_bg=pygame.color.Color(220, 220, 220),
            color_fg=pygame.color.Color(255, 122, 122),
            max_value=600,
        )

        self.player_energy_bar = DualBar(
            self.screen,
            position=(683, 706),
            position_type="topleft",
            width=96,
            height=52,
            color_bg=pygame.color.Color(220, 220, 220),
            color_fg=pygame.color.Color(122, 215, 255),
            max_value=self.player_max_energy,
        )

        self.enemy_health_bar = DualBar(
            self.screen,
            position=(566, 0),
            position_type="topleft",
            width=96,
            height=52,
            color_bg=pygame.color.Color(220, 220, 220),
            color_fg=pygame.color.Color(255, 122, 122),
            max_value=600,
            rotation=180
        )

        self.enemy_energy_bar = DualBar(
            self.screen,
            position=(683, 0),
            position_type="topleft",
            width=96,
            height=52,
            color_bg=pygame.color.Color(220, 220, 220),
            color_fg=pygame.color.Color(122, 215, 255),
            max_value=self.enemy_max_energy,
            rotation=180
        )

        # Text Boxes
        self.player_health_bar_text = TextBox(
            self.screen,
            position=(566, 706),
            width=96,
            height=52,
            font=Fonts.ger_font(30),
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
            font=Fonts.ger_font(30),
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
            font=Fonts.ger_font(30),
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
            font=Fonts.ger_font(30),
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
            font=Fonts.ger_font(30),
            color=(255, 255, 255),
            position_type="topleft",
            text_center="center",
            text="",
        )

        self.is_selecting = TextBox(
            self.screen,
            position=(1183, 711),
            position_type="topleft",
            width=153,
            height=41,
            font=Fonts.ger_font(35),
            color=(255, 255, 255),
            text="Selecting..."
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
            if event.type == CustomEvents.UI_STATE:
                # Access the dictionary attribute using vars()
                event_dict = vars(event)
                for state in event_dict.keys():
                    self.ui_state[state] = event_dict[state]
            if event.type == CustomEvents.CARD_ATTACK:
                self.pending_actions.extend([event])
                pygame.event.post(pygame.event.Event(
                    CustomEvents.UI_STATE, {"selecting": True}))
                pygame.event.post(pygame.event.Event(CustomEvents.CLOSE_POPUP))
            if event.type == CustomEvents.DEF_ATTACK:
                self.pending_actions.extend([event])
                pygame.event.post(pygame.event.Event(
                    CustomEvents.UI_STATE, {"selecting": True}))
                pygame.event.post(pygame.event.Event(CustomEvents.CLOSE_POPUP))
            if self.ui_state["selecting"] and event.type == CustomEvents.SLOT_CLICKED:
                self.pending_actions.append(event)

    def handle_action(self):
        if len(self.pending_actions) < 2:
            return
        approved = self.check_attack()
        if self.pending_actions[0].type == CustomEvents.DEF_ATTACK and approved:
            print(
                f"DEF_ATTACK, From: {self.pending_actions[0].slot} to {self.pending_actions[1].slot} with attack: {self.pending_actions[0].attack}")
        elif self.pending_actions[0].type == CustomEvents.CARD_ATTACK and approved:
            print(
                f"CARD_ATTACK, From: {self.pending_actions[0].slot} to {self.pending_actions[1].slot} with attack: {self.pending_actions[0].attack}")
        pygame.event.post(pygame.event.Event(
            CustomEvents.UI_STATE, {"selecting": False}))
        self.pending_actions.clear()

    def check_attack(self):
        attack = self.pending_actions[0].attack
        if self.pending_actions[0].slot == self.pending_actions[1].slot:
            if attack.target_mode.canself():
                return True
            else:
                logging.warn(
                    "Trying to inflict illegal attack on self. Cancelling attack.")
                return False
        return True

    # Toggle State

    def is_paused_toggle(self):
        self.ui_state["paused"] = not self.ui_state["paused"]

    def is_decked_toggle(self):
        self.ui_state["decked"] = not self.ui_state["decked"]

    def is_handed_toggle(self):
        self.ui_state["handed"] = not self.ui_state["handed"]

    def game_menu(self):
        # Check for Arena changes.
        if self.current_arena != handle.state["arena"].value:
            self.current_arena = handle.state["arena"].value
            self.bg_game_menu_image = MenuBackgrounds.bg_menu_images[
                min(self.current_arena, 4)
            ].convert_alpha()
            self.bg_game_menu_rect = self.bg_game_menu_image.get_rect(
                topleft=(0, 0))
        
        # Background elements
        self.screen.blit(self.bg_game_menu_image, self.bg_game_menu_rect)
        self.player_health_bar.render(self.player_health)
        self.player_energy_bar.render(self.player_energy)
        self.enemy_health_bar.render(self.enemy_health)
        self.enemy_energy_bar.render(self.enemy_energy)
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
            if self.deckback_button.answer() or self.escp_rel.update(pygame.event.get(pygame.KEYUP)):
                self.is_decked_toggle()
        self.hand_button.render()
        if self.hand_button.answer():
            self.is_handed_toggle()
        if self.ui_state["handed"]:
            self.screen.blit(self.bg_hand_menu_image, self.bg_hand_menu_rect)
            self.handback_button.render()
            if self.handback_button.answer() or self.escp_rel.update(pygame.event.get(pygame.KEYUP)):
                self.is_handed_toggle()

        # Toggles
        if self.escp_rel.update(search_event(super().events, pygame.KEYUP)):
            self.is_paused_toggle()
        if self.ui_state["paused"]:
            self.screen.blit(self.bg_pause_menu_image, self.bg_pause_menu_rect)
            self.pauseback_button.render()
            self.settings_button.render()
            self.surrender_button.render()
            if self.pauseback_button.answer() or self.escp_rel.update(pygame.event.get(pygame.KEYUP)):
                self.is_paused_toggle()
            elif self.surrender_button.answer():
                self.is_paused_toggle()
                self.revert_state(2)
        if self.ui_state["selecting"]:
            self.is_selecting.render()

        self.handle_events(super().events)
        self.handle_action()

    def state_manager_hook(self, app):
        if len(State.state_tree) >= 6:
            raise ValueError("Bro what?")
        elif State.state_tree[4] == self.local_options[0]:
            self.game_menu()

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
from UserInterface.card_handler import BoardManager, DeckManager, HandManager
from Assets.menu_assets import MenuBackgrounds, MenuButtons, Fonts, alpha_converter
from Assets.menu_assets import CardAssets
from SfxEngine.SoundEngine import sound_handle

def slottuple2index(slot: tuple) -> str:
    if len(slot) < 3:  # commander
        return slot[0] + "@"
    board = handle.get_state()[slot[0]]["board"]
    delta: int = 0
    l = len(board)
    while (
        delta < l
        and board[delta] is not None
        and board[delta]["name"] == "crossed_slot"
    ):
        delta += 1
    print(f"{board=}\n{delta=}\n{slot[2]-delta=}")
    return slot[0] + str(slot[2] - delta)


class GameMenu(State):
    def __init__(self, screen):
        self.game_state = handle.get_state()  # return placeholder before initialization
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
            "selecting": False,
        }
        self.pending_actions = []

        # Game Menu
        self.current_arena = self.game_state["arena"]
        self.bg_game_menu_image = MenuBackgrounds.bg_menu_images[min(self.current_arena, 4)].convert_alpha()
        self.bg_game_menu_rect = self.bg_game_menu_image.get_rect(topleft=(0, 0))
        
        self.turnbadge_down_image = MenuBackgrounds.bg_assets["turnbadge_down"]["img"].convert_alpha()
        self.turnbadge_down_rect = self.turnbadge_down_image.get_rect(topleft=(17, 0))
        self.turnbadge_up_image = MenuBackgrounds.bg_assets["turnbadge_up"]["img"].convert_alpha()
        self.turnbadge_up_rect = self.turnbadge_up_image.get_rect(topleft=(20, 704))

        # Hand
        self.hand_button = ImageButton(
            self.screen,
            True,
            image=alpha_converter(MenuButtons.button_assets["Hand"]["img"]),
            position_type="topleft",
            position=(296, 706),
        )
        self.hand_manager = HandManager(self.screen)
        # Deck
        self.deck_button = ImageButton(
            self.screen,
            True,
            image=alpha_converter(MenuButtons.button_assets["Deck"]["img"]),
            position_type="topleft",
            position=(824, 706),
        )

        self.deck_manager = DeckManager(self.screen, [])  # wip

        # Bars
        self.player_health_bar = DualBar(
            self.screen,
            position=(566, 706),
            position_type="topleft",
            width=96,
            height=52,
            color_bg=pygame.color.Color(220, 220, 220),
            color_fg=pygame.color.Color(255, 122, 122),
            max_value=self.game_state["local"]["commander"]["max_hp"],
        )

        self.player_energy_bar = DualBar(
            self.screen,
            position=(683, 706),
            position_type="topleft",
            width=96,
            height=52,
            color_bg=pygame.color.Color(220, 220, 220),
            color_fg=pygame.color.Color(122, 215, 255),
            max_value=self.game_state["local"]["max_energy"],
        )

        self.enemy_health_bar = DualBar(
            self.screen,
            position=(566, 0),
            position_type="topleft",
            width=96,
            height=52,
            color_bg=pygame.color.Color(220, 220, 220),
            color_fg=pygame.color.Color(255, 122, 122),
            max_value=self.game_state["remote"]["commander"]["max_hp"],
            rotation=180,
        )

        self.enemy_energy_bar = DualBar(
            self.screen,
            position=(683, 0),
            position_type="topleft",
            width=96,
            height=52,
            color_bg=pygame.color.Color(220, 220, 220),
            color_fg=pygame.color.Color(122, 215, 255),
            max_value=self.game_state["remote"]["max_energy"],
            rotation=180,
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
            position=(112, 713),
            width=76,
            height=35,
            font=Fonts.ger_font(30),
            color=(255, 255, 255),
            position_type="topleft",
            text_center="center",
            text="",
        )

        self.enemy_username_text = TextBox(
            self.screen,
            position=(112, 6),
            width=76,
            height=35,
            font=Fonts.ger_font(30),
            color=(255,255,255),
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
            text="Selecting...",
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
            image=alpha_converter(MenuButtons.button_assets["Settings"]["img"]),
            position_type="center",
            position=(SCREEN_CENTER[0], 392),
        )

        self.surrender_button = ImageButton(
            self.screen,
            True,
            image=alpha_converter(MenuButtons.button_assets["Surrender"]["img"]),
            postion_type="center",
            position=(SCREEN_CENTER[0], 490),
        )

        # Deck Menu
        self.bg_deck_menu_image = MenuBackgrounds.bg_assets["deck_menu_empty"][
            "img"
        ].convert_alpha()
        self.bg_deck_menu_rect = self.bg_deck_menu_image.get_rect(center=SCREEN_CENTER)

        # Hand Menu
        self.bg_hand_menu_image = MenuBackgrounds.bg_assets["hand_menu_empty"][
            "img"
        ].convert_alpha()
        self.bg_hand_menu_rect = self.bg_hand_menu_image.get_rect(center=SCREEN_CENTER)

        self.card_manager = BoardManager(
            self.screen, len(self.game_state["local"]["board"])
        )

        self.end_turn_btn = ImageButton(
            self.screen,
            pygame.event.Event(CustomEvents.END_TURN),
            image=MenuButtons.button_assets["Endturn"]["img"],
            position_type="topleft",
            position=(44, 645),
        )

    def handle_events(self, events):
        for event in events:
            if event.type == CustomEvents.UI_STATE:
                event_dict = vars(event)
                for state in event_dict.keys():
                    self.ui_state[state] = event_dict[state]
            if event.type == CustomEvents.CARD_ATTACK:
                self.pending_actions.extend([event])
                pygame.event.post(
                    pygame.event.Event(CustomEvents.UI_STATE, {"selecting": True})
                )
                pygame.event.post(pygame.event.Event(CustomEvents.CLOSE_POPUP))
            if event.type == CustomEvents.DEF_ATTACK:
                self.pending_actions.extend([event])
                pygame.event.post(
                    pygame.event.Event(CustomEvents.UI_STATE, {"selecting": True})
                )
                pygame.event.post(pygame.event.Event(CustomEvents.CLOSE_POPUP))
            if event.type == CustomEvents.ULTIMATE:
                self.pending_actions.extend([event])
                pygame.event.post(
                    pygame.event.Event(CustomEvents.UI_STATE, {"selecting": True})
                )
                pygame.event.post(pygame.event.Event(CustomEvents.CLOSE_POPUP))
            if event.type == CustomEvents.PLACE_CARD:
                self.pending_actions.extend([event])
                pygame.event.post(
                    pygame.event.Event(CustomEvents.UI_STATE, {"selecting": True})
                )
                self.is_handed_toggle()
            if event.type == CustomEvents.DISCARD_CARD:
                print(f"Discarded card at {event.hand_index}")
                handle.run_action(f"discard|{event.hand_index}")
            if event.type == CustomEvents.END_TURN:
                handle.run_action("endturn")
                print("Ended turn")

            if self.ui_state["selecting"] and event.type == CustomEvents.SLOT_CLICKED:
                if (
                    self.pending_actions[0].type == CustomEvents.PLACE_CARD
                    and event.empty
                    and "local" in event.slot
                ):
                    self.pending_actions.append(event)
                elif self.pending_actions[0].type in [CustomEvents.DEF_ATTACK, CustomEvents.CARD_ATTACK,CustomEvents.ULTIMATE] and not event.empty:
                    self.pending_actions.append(event)
                else:
                    logging.warn("Unsuported event")

    def handle_action(self):
        if len(self.pending_actions) < 2:
            return
        approved = self.check_attack()
        if self.pending_actions[0].type == CustomEvents.DEF_ATTACK and approved:
            print(
                f"DEF_ATTACK, From: {self.pending_actions[0].slot} to {self.pending_actions[1].slot} with attack: {self.pending_actions[0].attack}"
            )
            # leaving print for now, remove after testing

            #sound_handle("fire", "play", channel=8)

            user_slot = self.pending_actions[0].slot
            target_slot = self.pending_actions[1].slot
            if user_slot[1] == "board":
                handle.run_action(
                    f"attack|{slottuple2index(user_slot)}|0|{slottuple2index(target_slot)}"
                )
            else:
                handle.run_action(f"attack|ally@|0|{slottuple2index(target_slot)}")
        elif self.pending_actions[0].type == CustomEvents.CARD_ATTACK and approved:
            print(
                f"CARD_ATTACK, From: {self.pending_actions[0].slot} to {self.pending_actions[1].slot} with attack: {self.pending_actions[0].attack}"
            )


            user_slot = self.pending_actions[0].slot
            target_slot = self.pending_actions[1].slot
            handle.run_action(
                f"attack|{slottuple2index(user_slot)}|1|{slottuple2index(target_slot)}"
            )

        elif self.pending_actions[0].type == CustomEvents.ULTIMATE and approved:
            if (
                self.game_state[self.pending_actions[0].slot[0]][
                    self.pending_actions[0].slot[1]
                ]["ult_cost"]
                < self.game_state[self.pending_actions[0].slot[0]][
                    self.pending_actions[0].slot[1]
                ]["charges"]
            ):
                print(
                    f"ULTIMATE, From: {self.pending_actions[0].slot} to {self.pending_actions[1].slot} with attack: {self.pending_actions[0].attack}"
                )
            #sound_handle("ultimateattack", "play", channel=8)
            target_slot = self.pending_actions[1].slot
            handle.run_action(f"attack|ally@|1|{slottuple2index(target_slot)}")
        elif (
            self.pending_actions[0].type == CustomEvents.PLACE_CARD
            and self.pending_actions[1].empty
        ):
            print(
                f"Placed card {self.pending_actions[0].hand_index} to slot {self.pending_actions[1].slot}"
            )
            delta = 0
            board = self.game_state[self.pending_actions[1].slot[0]]["board"]
            l = len(board)
            while (
                delta < l
                and board[delta] is not None
                and board[delta]["name"] == "crossed_slot"
            ):
                delta += 1
            handle.run_action(
                f"place|{self.pending_actions[0].hand_index}|{self.pending_actions[1].slot[2]-delta}"
            )
        elif (
            self.pending_actions[0].type == CustomEvents.PLACE_CARD
            and not self.pending_actions[1].empty
        ):
            logging.warn(
                f"Trying to inflict illegal operation: Placing card on already occupied slot. ({self.pending_actions[0].hand_index} -> {self.pending_actions[1].slot})"
            )

        pygame.event.post(
            pygame.event.Event(CustomEvents.UI_STATE, {"selecting": False})
        )
        self.pending_actions.clear()

    def check_attack(self):
        try:
            attack = self.pending_actions[0].attack
            if self.pending_actions[0].slot == self.pending_actions[1].slot:
                if attack.target_mode.canself():
                    return True
                else:
                    logging.warn(
                        "Trying to inflict illegal attack on self. Cancelling attack."
                    )
                    return False
            if self.pending_actions[0].slot[1] == "commander":
                if attack.target_mode.cancommander():
                    return True
                else:
                    logging.warn(
                        "Trying to inflict illegal attack on commander. Cancelling attack."
                    )
                    return False
            return True
        except Exception:
            return False

    # Toggle State
    def is_paused_toggle(self):
        self.ui_state["paused"] = not self.ui_state["paused"]

    def is_decked_toggle(self):
        self.ui_state["decked"] = not self.ui_state["decked"]

    def is_handed_toggle(self):
        self.ui_state["handed"] = not self.ui_state["handed"]

    def game_menu(self):
        # Update game state
        self.game_state = handle.get_state()

        # Check for Arena changes.
        if self.current_arena != self.game_state["arena"]:
            self.current_arena = self.game_state["arena"]
            self.bg_game_menu_image = MenuBackgrounds.bg_menu_images[
                min(self.current_arena, 4)
            ].convert_alpha()
            self.bg_game_menu_rect = self.bg_game_menu_image.get_rect(topleft=(0, 0))

        # Background elements
        self.screen.blit(self.bg_game_menu_image, self.bg_game_menu_rect)
        self.player_username_text.render(self.game_state["local"]["name"])
        self.enemy_username_text.render(self.game_state["remote"]["name"])
        self.player_health_bar.render(self.game_state["local"]["commander"]["hp"])
        self.player_energy_bar.render(self.game_state["local"]["energy"])
        self.enemy_health_bar.render(self.game_state["remote"]["commander"]["hp"])
        self.enemy_energy_bar.render(self.game_state["remote"]["energy"])
        self.player_energy_bar_text.render(str(self.game_state["local"]["energy"]))
        self.enemy_energy_bar_text.render(str(self.game_state["remote"]["energy"]))
        self.player_health_bar_text.render(str(self.game_state["local"]["commander"]["hp"]))
        self.enemy_health_bar_text.render(str(self.game_state["remote"]["commander"]["hp"]))
        self.card_manager.render(super().events, self.ui_state, self.game_state)

        # User buttons
        self.deck_button.render()
        if self.deck_button.answer():
            self.is_decked_toggle()
        if self.ui_state["decked"]:
            self.deck_manager.render(super().events)

        self.hand_button.render()
        if self.hand_button.answer():
            self.is_handed_toggle()
        if self.ui_state["handed"]:
            self.hand_manager.render(self.game_state["local"]["hand"], super().events)

        # Toggles
        if self.escp_rel.update(search_event(super().events, pygame.KEYUP)):
            self.is_paused_toggle()
        if self.ui_state["paused"]:
            self.screen.blit(self.bg_pause_menu_image, self.bg_pause_menu_rect)
            self.pauseback_button.render()
            self.settings_button.render()
            self.surrender_button.render()
            if self.pauseback_button.answer() or self.escp_rel.update(
                pygame.event.get(pygame.KEYUP)
            ):
                self.is_paused_toggle()
            elif self.surrender_button.answer():
                self.is_paused_toggle()
                self.revert_state(2)
        if self.ui_state["selecting"]:
            self.is_selecting.render()

        self.handle_events(super().events)
        self.handle_action()
        if handle.get_state()["isactive"]:
            self.end_turn_btn.render()
            self.end_turn_btn.answer()
            self.screen.blit(self.turnbadge_up_image, self.turnbadge_up_rect)
        else:
            self.screen.blit(self.turnbadge_down_image, self.turnbadge_down_rect)

    def state_manager_hook(self, app):
        if len(State.state_tree) >= 6:
            raise ValueError("Bro what?")
        elif State.state_tree[4] == self.local_options[0]:
            self.game_menu()

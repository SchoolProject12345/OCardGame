from Assets.menu_assets import CardAssets
from UserInterface.OcgVision.vision_coordadapter import rect_grid
from UserInterface.ui_settings import SCREEN_CENTER
import pygame
from utility import search_event, cwd_path
import os
from Assets.menu_assets import (
    MenuBackgrounds,
    CardAssets,
    MenuButtons,
    Fonts,
    Sprites,
)
from UserInterface.OcgVision.vision_main import ImageButton, TextBox, DualBar
from UserInterface.event_library import CustomEvents
from Core.core_main import AbstractCard
import json
import logging


class BoardCardHolder:
    board_positions = {
        "remote": {
            "board": rect_grid((203, 225), "topleft", (940, 124), (7, 1), 12),
            "commander": pygame.rect.Rect(586, 56, 174, 135),
        },
        "local": {
            "board": rect_grid((203, 405), "topleft", (940, 124), (7, 1), 12),
            "commander": pygame.rect.Rect(586, 545, 174, 135),
        },
    }

    def __init__(
        self,
        screen: pygame.Surface,
        board_index: tuple[str, str, int] | tuple[str, str],
        is_commander: bool = False,
        **kwargs,
    ) -> None:
        self.screen = screen
        self.board_index = board_index
        self.card_active = kwargs.get("card_active", True)
        self.card_open = kwargs.get("card_open", False)
        self.is_commander = is_commander
        if self.is_commander:
            self.position = BoardCardHolder.board_positions[board_index[0]][
                board_index[1]
            ]
        else:
            self.position = BoardCardHolder.board_positions[board_index[0]][
                board_index[1]
            ][board_index[2]]

    def render(
        self,
        mouse_pos: tuple[int, int],
        mousebuttondown: pygame.MOUSEBUTTONDOWN,
        card: str,
        active=True,
    ):
        self.mouse_pos = mouse_pos
        self.mousebuttondown = mousebuttondown
        self.active = active
        self.card = card

        if self.is_commander:
            self.render_commander()
        else:
            self.render_card()

    def render_commander(self):
        if self.active:
            self.check_clicked(self.mouse_pos, self.mousebuttondown)
        if self.card["name"] in CardAssets.commander_sprites:
            self.card_img = CardAssets.commander_sprites[self.card["name"]]["img"]
        else:
            self.card_img = CardAssets.card_sprites["card_not_found"]["img"]
        self.screen.blit(self.card_img[0], self.position)

    def render_card(self):
        if self.card == None:
            self.card = {"name": "misc_empty"}
        self.card_perm = self.card["name"] != "crossed_slot"
        if self.active and self.card_perm:
            self.check_clicked(self.mouse_pos, self.mousebuttondown)
        if self.card["name"] in CardAssets.card_sprites:
            self.card_img = CardAssets.card_sprites[self.card["name"]]["img"]
        else:
            self.card_img = CardAssets.card_sprites["card_not_found"]["img"]
        self.screen.blit(self.card_img[0], self.position)

    def check_clicked(
        self, mouse_pos: tuple[int, int], mousebuttondown: pygame.MOUSEBUTTONDOWN
    ):
        if self.position.collidepoint(mouse_pos) and mousebuttondown:
            if self.card["name"] == "misc_empty":
                self.empty_slot = True
            else:
                self.empty_slot = False
            pygame.event.post(
                pygame.event.Event(
                    CustomEvents.SLOT_CLICKED,
                    {"slot": self.board_index, "empty": self.empty_slot},
                )
            )


class BoardManager:
    def __init__(self, screen, n_cards):
        self.screen = screen
        self.n_cards = n_cards
        self.show_popup = False
        self.card_slots = {
            "local": {"board": [], "hand": [], "deck": [], "commander": []},
            "remote": {"board": [], "hand": [], "deck": [], "commander": []},
        }
        for n in range(self.n_cards):
            self.card_slots["local"]["board"].append(
                BoardCardHolder(self.screen, ("local", "board", n))
            )
            self.card_slots["remote"]["board"].append(
                BoardCardHolder(self.screen, ("remote", "board", n))
            )
        for slot_type in ["local", "remote"]:
            self.card_slots[slot_type]["commander"].append(
                BoardCardHolder(
                    self.screen, (slot_type, "commander"), is_commander=True
                )
            )
            self.card_slots[slot_type]["commander"].append(
                BoardCardHolder(
                    self.screen, (slot_type, "commander"), is_commander=True
                )
            )

    def render(self, events, ui_gamestate, game_state):
        self.game_state = game_state
        self.ui_gamestate = ui_gamestate
        self.mouse_down = search_event(events, pygame.MOUSEBUTTONDOWN)
        self.mouse_pos = pygame.mouse.get_pos()
        self.check_active_slots()
        self.update_board()
        self.update_popup(
            search_event(events, [CustomEvents.CLOSE_POPUP, CustomEvents.SLOT_CLICKED])
        )

    def update_popup(self, popup_event):
        for event in popup_event:
            if (
                CustomEvents.SLOT_CLICKED == event.type
                and not event.empty
                and not self.ui_gamestate["selecting"]
            ):
                self.popup_info = event.slot
                self.generate_popup(self.popup_info)
                pygame.event.post(
                    pygame.event.Event(CustomEvents.UI_STATE, {"popped": True})
                )
                self.show_popup = True
            elif CustomEvents.CLOSE_POPUP == event.type:
                self.show_popup = False
                pygame.event.post(
                    pygame.event.Event(CustomEvents.UI_STATE, {"popped": False})
                )
        if self.show_popup:
            self.render_popup()

    def generate_popup(self, slot):
        if len(slot) > 2:
            self.popup_card(slot)
        else:
            self.popup_commander(slot)

    def popup_commander(self, slot):
        self.popup_slot = slot
        self.card_state = self.get_card(self.popup_slot)
        self.card_info = AbstractCard.from_id(self.card_state["name"])
        self.popup_bg = MenuBackgrounds.bg_assets["attack_popup_empty"]["img"]
        self.popup_bg_rect = self.popup_bg.get_rect(center=SCREEN_CENTER)
        popup_name = self.get_card(self.popup_slot)["name"]
        self.popup_txt = []
        if popup_name in CardAssets.commander_sprites.keys():
            self.popup_card_img = CardAssets.commander_sprites[popup_name]["img"][1]
        else:
            self.popup_card_img = CardAssets.commander_sprites["card_not_found"]["img"][
                1
            ]
            self.popup_txt.append(
                TextBox(
                    self.screen,
                    (837, 215),
                    132,
                    29,
                    Fonts.ger_font(22),
                    (200, 200, 200),
                    text=f"ID: {popup_name}",
                )
            )

        self.health_box = Sprites.box_assets["card_health"]["img"]
        self.popup_btns = [
            ImageButton(
                self.screen,
                pygame.event.Event(CustomEvents.CLOSE_POPUP),
                image=MenuButtons.button_assets["CloseMenu"]["img"],
                position_type="topleft",
                position=(641, 502),
            )
        ]
        self.popup_txt.extend(
            [
                TextBox(
                    self.screen,
                    (837, 265),
                    132,
                    29,
                    Fonts.ger_font(22),
                    (255, 255, 255),
                    "topleft",
                    "center",
                    f"{self.card_state['hp']}/{self.card_state['max_hp']} HP",
                ),
                TextBox(
                    self.screen,
                    (855, 409),
                    132,
                    29,
                    Fonts.ger_font(22),
                    (255, 255, 255),
                    position_type="topleft",
                    text_center="center",
                    text=f"{self.card_state['charges']}/{self.card_state['ult_cost']} DMG",
                ),
                TextBox(
                    self.screen,
                    (791, 409),
                    56,
                    29,
                    Fonts.ger_font(22),
                    (255, 255, 255),
                    position_type="topleft",
                    text_center="center",
                    text=f"{self.card_state['charges'] // self.card_state['ult_cost']}",
                ),
            ]
        )
        if self.popup_slot[0] == "local":
            self.popup_btns.extend(
                [
                    ImageButton(
                        self.screen,
                        pygame.event.Event(
                            CustomEvents.DEF_ATTACK,
                            {
                                "slot": self.popup_slot,
                                "attack": self.card_info.attacks[0],
                            },
                        ),
                        image=MenuButtons.button_assets["DefCardAttack"]["img"],
                        position_type="topleft",
                        position=(641, 353),
                    ),
                    ImageButton(
                        self.screen,
                        pygame.event.Event(
                            CustomEvents.ULTIMATE,
                            {
                                "slot": self.popup_slot,
                                "attack": self.card_info.attacks[1],
                            },
                        ),
                        image=MenuButtons.button_assets["UltimateStatus"]["img"],
                        position_type="topleft",
                        position=(641, 403),
                    ),
                ]
            )
            self.popup_txt.extend(
                [
                    TextBox(
                        self.screen,
                        (812, 359),
                        90,
                        29,
                        Fonts.ger_font(22),
                        (255, 255, 255),
                        "topleft",
                        "center",
                        text=f"{self.card_info.attacks[0].cost} NRG",
                    ),
                    TextBox(
                        self.screen,
                        (911, 359),
                        90,
                        29,
                        Fonts.ger_font(22),
                        (255, 255, 255),
                        "topleft",
                        "center",
                        text=f"{self.card_info.attacks[0].power} DMG",
                    ),
                ]
            )
        else:
            self.ultimate_box = Sprites.box_assets["ultimate_status"]["img"]
        if self.card_state["state"] != "default":
            self.state_icon = Sprites.states_assets[self.card_state["state"]]["img"]
            self.state_icon_rect = self.state_icon.get_rect(topright=(1017, 184))

    def popup_card(self, slot):
        self.popup_slot = slot
        self.card_state = self.get_card(self.popup_slot)
        self.card_info = AbstractCard.from_id(self.card_state["name"])
        self.popup_bg = MenuBackgrounds.bg_assets["attack_popup_empty"]["img"]
        self.popup_bg_rect = self.popup_bg.get_rect(center=SCREEN_CENTER)
        popup_name = self.get_card(self.popup_slot)["name"]
        self.popup_txt = []
        if popup_name in CardAssets.card_sprites.keys():
            self.popup_card_img = CardAssets.card_sprites[popup_name]["img"][1]
        else:
            self.popup_card_img = CardAssets.card_sprites["card_not_found"]["img"][1]
            self.popup_txt.append(
                TextBox(
                    self.screen,
                    (837, 215),
                    132,
                    29,
                    Fonts.ger_font(22),
                    (200, 200, 200),
                    text=f"ID: {popup_name}",
                )
            )

        self.health_box = Sprites.box_assets["card_health"]["img"]
        self.popup_btns = [
            ImageButton(
                self.screen,
                pygame.event.Event(CustomEvents.CLOSE_POPUP),
                image=MenuButtons.button_assets["CloseMenu"]["img"],
                position_type="topleft",
                position=(641, 502),
            )
        ]
        self.popup_txt.append(
            TextBox(
                self.screen,
                (837, 265),
                132,
                29,
                Fonts.ger_font(22),
                (255, 255, 255),
                "topleft",
                "center",
                f"{self.card_state['hp']}/{self.card_state['max_hp']} HP",
            )
        )

        if self.popup_slot[0] == "local":
            self.popup_btns.extend(
                [
                    ImageButton(
                        self.screen,
                        pygame.event.Event(
                            CustomEvents.DEF_ATTACK,
                            {
                                "slot": self.popup_slot,
                                "attack": self.card_info.attacks[0],
                            },
                        ),
                        image=MenuButtons.button_assets["DefCardAttack"]["img"],
                        position_type="topleft",
                        position=(641, 353),
                    ),
                    ImageButton(
                        self.screen,
                        pygame.event.Event(
                            CustomEvents.CARD_ATTACK,
                            {
                                "slot": self.popup_slot,
                                "attack": self.card_info.attacks[1],
                            },
                        ),
                        image=MenuButtons.button_assets["CardAttack"]["img"],
                        position_type="topleft",
                        position=(641, 403),
                    ),
                ]
            )
            self.popup_txt.extend(
                [
                    TextBox(
                        self.screen,
                        (812, 359),
                        90,
                        29,
                        Fonts.ger_font(22),
                        (255, 255, 255),
                        "topleft",
                        "center",
                        text=f"{self.card_info.attacks[0].cost} NRG",
                    ),
                    TextBox(
                        self.screen,
                        (911, 359),
                        90,
                        29,
                        Fonts.ger_font(22),
                        (255, 255, 255),
                        "topleft",
                        "center",
                        text=f"{self.card_info.attacks[0].power} DMG",
                    ),
                    TextBox(
                        self.screen,
                        (812, 409),
                        90,
                        29,
                        Fonts.ger_font(22),
                        (255, 255, 255),
                        "topleft",
                        "center",
                        text=f"{self.card_info.attacks[1].cost} NRG",
                    ),
                    TextBox(
                        self.screen,
                        (911, 409),
                        90,
                        29,
                        Fonts.ger_font(22),
                        (255, 255, 255),
                        "topleft",
                        "center",
                        text=f"{self.card_info.attacks[1].power} DMG",
                    ),
                ]
            )

        if self.card_state["state"] != "default":
            self.state_icon = Sprites.states_assets[self.card_state["state"]]["img"]
            self.state_icon_rect = self.state_icon.get_rect(topright=(1017, 184))

    def render_popup(self):
        self.screen.blit(self.popup_bg, self.popup_bg_rect)
        self.screen.blit(self.health_box, (641, 259))
        self.screen.blit(self.popup_card_img, (295, 179))
        if self.card_state["state"] != "default":
            self.screen.blit(self.state_icon, self.state_icon_rect)
        if self.popup_slot[0] == "remote" and len(self.popup_slot) == 2:
            self.screen.blit(self.ultimate_box, (641, 403))
        for btn in self.popup_btns:
            btn.render()
            btn.answer()
        for txt in self.popup_txt:
            txt.render()

    def update_board(self):
        for index, slot in enumerate(self.card_slots["local"]["board"]):
            self.slot_card = self.get_card(("local", "board", index))
            slot.render(
                self.mouse_pos,
                self.mouse_down,
                card=self.slot_card,
                active=self.board_active,
            )
            if self.slot_card != None and self.slot_card["name"] != "crossed_slot":
                health_bar = DualBar(
                    self.screen,
                    (
                        BoardCardHolder.board_positions["local"]["board"][index][0] + 5,
                        BoardCardHolder.board_positions["local"]["board"][index][1]
                        + 130,
                    ),
                    "topleft",
                    7,
                    117,
                    (217, 217, 217),
                    (255, 122, 122),
                    self.slot_card["max_hp"],
                    -90,
                )
                health_bar.render(self.slot_card["hp"])

        for index, slot in enumerate(self.card_slots["remote"]["board"]):
            self.slot_card = self.get_card(("remote", "board", index))
            slot.render(
                self.mouse_pos,
                self.mouse_down,
                card=self.slot_card,
                active=self.board_active,
            )
            if self.slot_card != None and self.slot_card["name"] != "crossed_slot":
                health_bar = DualBar(
                    self.screen,
                    (
                        BoardCardHolder.board_positions["remote"]["board"][index][0]
                        + 5,
                        BoardCardHolder.board_positions["remote"]["board"][index][1]
                        - 13,
                    ),
                    "topleft",
                    7,
                    117,
                    (217, 217, 217),
                    (255, 122, 122),
                    self.slot_card["max_hp"],
                    -90,
                )
                health_bar.render(self.slot_card["hp"])

        for slot_type in ["local", "remote"]:
            self.card_slots[slot_type]["commander"][0].render(
                self.mouse_pos,
                self.mouse_down,
                card=self.get_card((slot_type, "commander")),
                active=self.board_active,
            )

    def check_active_slots(self):
        self.board_active = True
        if (
            self.ui_gamestate["paused"]
            or self.ui_gamestate["decked"]
            or self.ui_gamestate["handed"]
            or self.ui_gamestate["popped"]
        ):
            self.board_active = False

    def get_card(self, index: tuple[str, str, int]):
        if len(index) == 3:
            if self.game_state[index[0]][index[1]][index[2]] != None:
                return self.game_state[index[0]][index[1]][index[2]]
            else:
                return None
        elif len(index) == 2:
            if self.game_state[index[0]][index[1]] != None:
                return self.game_state[index[0]][index[1]]
            else:
                return None


class CardInfoPopup:
    def __init__(self, screen, position: tuple) -> None:
        self.screen = screen
        self.position = (496, 88)

        self.back_btn = ImageButton(
            self.screen,
            pygame.event.Event(CustomEvents.INFO_POPUP, {"state": False}),
            image=MenuButtons.button_assets["Back"]["img"],
            position_type="topleft",
            position=(581, 526),
        )

    def render(self, card_id: str):
        if card_id in CardAssets.card_sprites.keys():
            self.card_img = CardAssets.card_sprites[card_id]["img"][1]
        else:
            self.card_img = CardAssets.card_sprites["card_not_found"]["img"][1]
        self.screen.blit(Sprites.box_assets["card_info_popup"]["img"], self.position)
        self.screen.blit(self.card_img, (548, 111))
        self.back_btn.answer()
        self.back_btn.render()


class DeckCardHolder:
    def __init__(self, screen: pygame.Surface, rect_value: pygame.Rect):
        self.main_screen = screen
        self.rect_value = rect_value
        self.active = True

    def render(self, mouse_pos, is_m_btn_down, card_id: str, active: bool):
        self.card_id = card_id
        if active:
            self.check_clicked(mouse_pos, is_m_btn_down)
        self.card_img = CardAssets.card_sprites[card_id]["img"][0]
        self.main_screen.blit(self.card_img, self.rect_value)

    def check_clicked(self, mouse_pos, is_m_btn_down):
        if self.rect_value.collidepoint(mouse_pos) and is_m_btn_down:
            pygame.event.post(
                pygame.event.Event(
                    CustomEvents.INFO_POPUP, {"state": True, "card_id": self.card_id}
                )
            )
            return True
        return False


class DeckManager:
    def __init__(self, screen, deck: list):
        self.screen = screen
        self.deck_bg = MenuBackgrounds.bg_assets["deck_menu_empty"]["img"]
        self.deck = deck
        self.deck_grid = rect_grid((326, 148), "topleft", (696, 410), (5, 3), 10, 10)
        if len(self.deck) != len(self.deck_grid):
            logging.error("Deck size does not match grid size")
        self.deck_holders = [
            DeckCardHolder(self.screen, rect_value) for rect_value in self.deck_grid
        ]
        self.back_btn = ImageButton(
            self.screen,
            pygame.event.Event(CustomEvents.UI_STATE, {"decked": False}),
            image=MenuButtons.button_assets["Back"]["img"],
            position_type="topleft",
            position=(545, 587),
        )
        self.show_info = False
        self.info_popup = CardInfoPopup(self.screen, (469, 88))

    def render(self, events):
        self.screen.blit(self.deck_bg, (209, 38))
        self.render_deck(events)
        self.handle_info(events)

    def render_deck(self, events):
        mouse_pos = pygame.mouse.get_pos()
        m_btn_down = search_event(events, pygame.MOUSEBUTTONDOWN)
        for index, card_id in enumerate(self.deck):
            self.deck_holders[index].render(
                mouse_pos,
                m_btn_down,
                card_id,
                not self.show_info,
            )
        if not self.show_info:
            self.back_btn.answer()
            self.back_btn.render()

    def handle_info(self, events):
        for event in events:
            if event.type == CustomEvents.INFO_POPUP:
                self.show_info = event.state
                if self.show_info:
                    self.card_info = event.card_id

        if self.show_info:
            self.info_popup.render(self.card_info)


class HandManager:
    def __init__(
        self,
        screen,
    ) -> None:
        self.screen = screen
        self.bg_img = MenuBackgrounds.bg_assets["hand_menu_empty"]["img"]
        self.back_btn = ImageButton(
            self.screen,
            pygame.event.Event(CustomEvents.UI_STATE, {"handed": False}),
            image=MenuButtons.button_assets["Back"]["img"],
            position_type="topleft",
            position=(571, 519),
        )
        self.hand = []
        self.hand_holders = [HandGroup(self.screen, index) for index in range(6)]
        self.info_pop = CardInfoPopup(self.screen, (469, 88))
        self.info_card = None
        self.show_info = False

    def render(self, hand: list, events):
        self.screen.blit(self.bg_img, (241, 163))
        if self.hand != hand:
            self.update_hand(hand)
        for event in events:
            if event.type == CustomEvents.INFO_POPUP:
                if event.state:
                    self.info_card = event.card_id
                    self.show_info = True
                elif event.state is False:
                    self.show_info = False

        self.render_hand(
            [pygame.mouse.get_pos(), search_event(events, [pygame.MOUSEBUTTONDOWN])]
        )
        self.back_btn.render()
        self.back_btn.answer(not self.show_info)

        if self.show_info:
            self.info_pop.render(self.info_card)

    def update_hand(self, hand):
        self.hand = hand
        for index, holder in enumerate(self.hand_holders):
            holder.update(self.hand[index])

    def render_hand(self, events):
        for holder in self.hand_holders:
            holder.render(events[0], events[1])


class HandGroup:
    hand_slots = rect_grid((254, 296), "topleft", (820, 125), (6, 1), 14)

    def __init__(
        self,
        screen,
        index,
    ):
        self.screen = screen
        self.index = index
        self.card_position = HandGroup.hand_slots[index]
        self.place_position = (HandGroup.hand_slots[index].x, 432)
        self.discard_position = (HandGroup.hand_slots[index].x, 452)
        self.btns = [
            ImageButton(
                self.screen,
                pygame.event.Event(CustomEvents.PLACE_CARD, {"hand_index": self.index}),
                image=MenuButtons.button_assets["Place"]["img"],
                position_type="topleft",
                position=self.place_position,
            ),
            ImageButton(
                self.screen,
                pygame.event.Event(
                    CustomEvents.DISCARD_CARD, {"hand_index": self.index}
                ),
                image=MenuButtons.button_assets["Discard"]["img"],
                position_type="topleft",
                position=self.discard_position,
            ),
        ]

    def update(self, card_id):
        self.card_id = card_id
        if card_id in CardAssets.card_sprites.keys():
            self.card_img = CardAssets.card_sprites[card_id]["img"][0]
        else:
            self.card_img = CardAssets.card_sprites["card_not_found"]["img"][0]

    def render(self, mouse_pos, mousebuttondown):
        self.mouse_pos = mouse_pos
        self.mousebuttondown = mousebuttondown
        self.check_clicked()
        self.screen.blit(self.card_img, self.card_position)
        if not self.card_id in ["crossed_slot", "misc_empty"]:
            for btn in self.btns:
                btn.render()
                btn.answer()

    def check_clicked(self):
        if self.card_position.collidepoint(self.mouse_pos) and self.mousebuttondown:
            pygame.event.post(
                pygame.event.Event(
                    CustomEvents.INFO_POPUP, {"state": True, "card_id": self.card_id}
                )
            )
            return True
        return False

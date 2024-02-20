from Assets.menu_assets import CardAssets
from UserInterface.OcgVision.vision_coordadapter import rect_grid
from UserInterface.ui_settings import SCREEN_CENTER
import pygame
from utility import search_event
from Assets.menu_assets import MenuBackgrounds, CardAssets, MenuButtons
from UserInterface.OcgVision.vision_main import ImageButton
from UserInterface.event_library import CustomEvents


class CardHolder:
    board_positions = {
        "remote": {"board": rect_grid((203, 225), "topleft", (940, 124), (7, 1), 12)},
        "local": {"board": rect_grid((203, 405), "topleft", (940, 124), (7, 1), 12)},
    }

    def __init__(
        self, screen: pygame.Surface, board_index: tuple[str, str, int], **kwargs
    ) -> None:
        self.screen = screen
        self.board_index = board_index
        self.card_active = kwargs.get("card_active", True)
        self.card_open = kwargs.get("card_open", False)
        self.position = CardHolder.board_positions[board_index[0]][board_index[1]][
            board_index[2]
        ]

    def render(
        self,
        mouse_pos: tuple[int, int],
        mousebuttondown: pygame.MOUSEBUTTONDOWN,
        card_id: str = "MiscEmpty",
        active=True,
    ):
        self.card_id = card_id
        if self.card_id == None:
            self.card_id = "MiscEmpty"
        if active and self.card_id != "MiscEmpty":
            self.check_clicked(mouse_pos, mousebuttondown)
        self.card_img = CardAssets.card_sprites[self.card_id]["img"]
        self.screen.blit(self.card_img[0], self.position)

    def check_clicked(
        self, mouse_pos: tuple[int, int], mousebuttondown: pygame.MOUSEBUTTONDOWN
    ):
        if self.position.collidepoint(mouse_pos) and mousebuttondown:
            pygame.event.post(pygame.event.Event(
                CustomEvents.SLOT_CLICKED, {"slot": self.board_index}))


class CardManager:
    def __init__(self, screen, n_cards):
        self.screen = screen
        self.n_cards = n_cards
        self.show_popup = False
        self.card_slots = {
            "local": {"board": [], "hand": [], "deck": []},
            "remote": {"board": [], "hand": [], "deck": []},
        }
        for n in range(self.n_cards):
            self.card_slots["local"]["board"].append(
                CardHolder(self.screen, ("local", "board", n))
            )
            self.card_slots["remote"]["board"].append(
                CardHolder(self.screen, ("remote", "board", n))
            )

    def render(self, events, ui_gamestate, game_state):
        self.game_state = game_state
        self.ui_gamestate = ui_gamestate
        self.mouse_down = search_event(events, pygame.MOUSEBUTTONDOWN)
        self.mouse_pos = pygame.mouse.get_pos()
        self.check_active_slots()
        self.update_board()
        self.update_popup(search_event(
            events, [CustomEvents.CLOSE_POPUP, CustomEvents.SLOT_CLICKED]))

    def update_popup(self, popup_event):
        for event in popup_event:
            if CustomEvents.SLOT_CLICKED == event.type:
                self.popup_info = event.slot
                self.generate_popup(self.popup_info)
                pygame.event.post(pygame.event.Event(
                    CustomEvents.UI_STATE, {"popped": True}))
                self.show_popup = True
            elif CustomEvents.CLOSE_POPUP == event.type:
                self.show_popup = False
                pygame.event.post(pygame.event.Event(
                    CustomEvents.UI_STATE, {"popped": False}))
        if self.show_popup:
            self.render_popup()

    def generate_popup(self, slot):
        self.popup_bg = MenuBackgrounds.bg_assets["attack_popup_empty"]["img"]
        self.popup_bg_rect = self.popup_bg.get_rect(center=SCREEN_CENTER)
        self.popup_card_img = CardAssets.card_sprites[self.get_card(
            slot)]["img"][1]
        self.popup_btns = [
            ImageButton(
                self.screen, True, image=MenuButtons.button_assets["DefCardAttack"]["img"], position_type="topleft", position=(641, 288)),
            ImageButton(
                self.screen, True, image=MenuButtons.button_assets["CardAttack"]["img"], position_type="topleft", position=(641, 338)),
            ImageButton(
                self.screen, pygame.event.Event(CustomEvents.CLOSE_POPUP), image=MenuButtons.button_assets["CloseMenu"]["img"], position_type="topleft", position=(641, 502)
            )
        ]

    def render_popup(self):
        self.screen.blit(self.popup_bg, self.popup_bg_rect)
        self.screen.blit(self.popup_card_img, (295, 179))
        for btn in self.popup_btns:
            btn.render()
            btn.answer()

    def update_board(self):
        for index, slot in enumerate(self.card_slots["local"]["board"]):
            slot.render(
                self.mouse_pos,
                self.mouse_down,
                card_id=self.get_card(("local", "board", index)),
                active=self.board_active,
            )
        for index, slot in enumerate(self.card_slots["remote"]["board"]):
            slot.render(
                self.mouse_pos,
                self.mouse_down,
                card_id=self.get_card(("remote", "board", index)),
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
        if self.game_state[index[0]][index[1]][index[2]] != None:
            return self.game_state[index[0]][index[1]][index[2]]["name"]
        else:
            return None

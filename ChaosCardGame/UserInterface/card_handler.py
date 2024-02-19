from Assets.menu_assets import CardAssets
from UserInterface.OcgVision.vision_coordadapter import rect_grid
from UserInterface.ui_settings import SCREEN_CENTER
import pygame
from utility import search_event
from Assets.menu_assets import MenuBackgrounds
from UserInterface.event_library import fetch_event


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
        card_id: str = "misc_empty",
        active=True,
    ):
        self.card_id = card_id
        if self.card_id == None:
            self.card_id = "misc_empty"
        if active and self.card_id != "misc_empty":
            self.check_clicked(mouse_pos, mousebuttondown)
        self.card_img = CardAssets.card_sprites[self.card_id]["processed_img"]
        self.screen.blit(self.card_img[0], self.position)

    def check_clicked(
        self, mouse_pos: tuple[int, int], mousebuttondown: pygame.MOUSEBUTTONDOWN
    ):
        if self.position.collidepoint(mouse_pos) and mousebuttondown:
            pygame.event.post(
                fetch_event("SLOT_CLICKED", {"slot": self.board_index})
            )


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
        self.update_popup(search_event(events, fetch_event("SLOT_CLICKED", raw=True)))

    def update_popup(self, SLOT_CLICKED):

        if SLOT_CLICKED :
            self.show_popup = True
            self.displayed_card_info = SLOT_CLICKED
            pygame.event.post(fetch_event("UI_STATE", {"popped": True}))

        if self.show_popup:
            self.popup_bg = MenuBackgrounds.bg_assets["card_popup_empty"][
                "processed_img"
            ]
            self.popup_bg_rect = self.popup_bg.get_rect(center=SCREEN_CENTER)
            self.screen.blit(self.popup_bg, self.popup_bg_rect)

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
                card_id=self.get_card(("local", "board", index)),
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

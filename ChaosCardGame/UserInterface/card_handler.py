from Assets.menu_assets import CardAssets
from UserInterface.OcgVision.vision_coordadapter import rect_grid
import pygame


class CardHolder:
    board_positions = {
        "remote": rect_grid((203, 225), "topleft", (940, 124), (7, 1), 12),
        "local": rect_grid((203, 405), "topleft", (940, 124), (7, 1), 12),
    }

    def __init__(
        self,
        screen: pygame.Surface,
        board_index: tuple[str, int],
        board_type: str,
        **kwargs
    ) -> None:
        self.screen = screen
        self.board_index = board_index
        self.board_type = board_type
        self.card_active = kwargs.get("card_active", True)
        self.card_open = kwargs.get("card_open", True)
        self.position = CardHolder.board_positions[board_index[0]][board_index[1]]

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
        if active:
            self.check_clicked(mouse_pos, mousebuttondown)
        self.card_img = CardAssets.card_sprites[self.card_id]["processed_img"]
        if self.card_open:
            self.screen.blit(self.card_img[0], self.position)
        else:
            pass

    def toggle_active(self, state: bool = 0):
        if type(state) != int:
            self.card_open = state
        else:
            self.card_open = not self.card_open

    def check_clicked(
        self, mouse_pos: tuple[int, int], mousebuttondown: pygame.MOUSEBUTTONDOWN
    ):
        if self.position.collidepoint(mouse_pos) and mousebuttondown:
            print("Card clicked: ", self.board_index)


class CardManager:
    def __init__(self, screen, n_cards):
        self.screen = screen
        self.n_cards = n_cards
        self.card_slots = {
            "local": {"board": [], "hand": [], "deck": []},
            "remote": {"board": [], "hand": [], "deck": []},
        }
        for n in range(self.n_cards):
            self.card_slots["local"]["board"].append(
                CardHolder(self.screen, ("local", n), "board")
            )
            self.card_slots["remote"]["board"].append(
                CardHolder(self.screen, ("remote", n), "board")
            )

    def render(self, mouse_pos, mouse_down, ui_gamestate, game_state):
        self.game_state = game_state
        self.ui_gamestate = ui_gamestate
        self.check_active_slots()
        for index, slot in enumerate(self.card_slots["local"]["board"]):
            slot.render(
                mouse_pos,
                mouse_down,
                card_id=self.get_card(("local", "board", index)),
                active=self.board_active,
            )
        for index, slot in enumerate(self.card_slots["remote"]["board"]):
            slot.render(
                mouse_pos,
                mouse_down,
                card_id=self.get_card(("local", "board", index)),
                active=self.board_active,
            )

    def check_active_slots(self):
        self.board_active = True
        if (
            self.ui_gamestate["paused"]
            or self.ui_gamestate["decked"]
            or self.ui_gamestate["handed"]
        ):
            self.board_active = False

    def get_card(self, index: tuple[str, str, int]):
        if self.game_state[index[0]][index[1]][index[2]] != None:
            return self.game_state[index[0]][index[1]][index[2]]["name"]
        else:
            return None

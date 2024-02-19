from Assets.menu_assets import CardAssets
from UserInterface.OcgVision.vision_coordadapter import rect_grid
import pygame


class CardHolder:
    board_positions = {
        "remote": rect_grid((271, 225), "topleft", (804, 124), (6, 1), 12),
        "local": rect_grid((271, 405), "topleft", (804, 124), (6, 1), 12),
    }

    def __init__(
        self, screen: pygame.Surface, board_index: tuple[str,int], board_type: str, **kwargs
    ) -> None:
        self.screen = screen
        self.board_index = board_index
        self.board_type = board_type
        self.card_active = kwargs.get("card_active", True)
        self.card_open = kwargs.get("card_open", True)
        self.position = CardHolder.board_positions[board_index[0]][board_index[1]]

    def render(self, card_id: str = "misc_empty"):
        self.card_id = card_id
        self.card_img = CardAssets.card_sprites[self.card_id]["processed_img"]
        if self.card_open:
            self.screen.blit(self.card_img[1], self.position)
        else:
            self.screen.blit(self.card_img[0], self.position)

    def toggle_active(self, state: bool = 0):
        if type(state) != int:
            self.card_open = state
        else:
            self.card_open = not self.card_open

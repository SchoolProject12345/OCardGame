from Assets.menu_assets import CardAssets
import pygame


class CardHolder:
    def __init__(
        self, screen: pygame.Surface, board_index: int, board_type: str, **kwargs
    ) -> None:
        self.screen = screen
        self.board_index = board_index
        self.board_type = board_type
        self.card_active = kwargs.get("card_active", True)
        self.card_open = kwargs.get("card_open", True)

    def render(self, position, card_id: str = "misc_empty"):
        self.card_id = card_id
        self.card_img = CardAssets.card_sprites[self.card_id]["processed_img"]
        if self.card_open:
            self.screen.blit(self.card_img[1], (100, 100))
        else:
            self.screen.blit(self.card_img[0], (100, 100))

    def toggle_active(self, state: bool = 0):
        if type(state) != int:
            self.card_open = state
        else:
            self.card_open = not self.card_open

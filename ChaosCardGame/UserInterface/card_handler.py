from Assets.menu_assets import CardAssets
import pygame


class CardHolder:
    def __init__(
        self,screen: pygame.Surface, board_index: int, board_type: str, card_id: str = "", **kwargs
    ) -> None:
        self.screen = screen
        self.board_index = board_index
        self.board_type = board_type
        self.card_id = card_id
        self.card_img = CardAssets.card_sprites[card_id]["processed_img"]
        print(self.card_img)
        self.card_active = kwargs.get("card_active", True)
        self.card_open = kwargs.get("card_open", True)

    def render(self,position:pygame.Rect):
        
        if self.card_open:
            self.screen.blit(self.card_img[1],(100,100))
        else:
            self.screen.blit(self.card_img[0],(100,100))
    
    def toggle_active(self,state:bool=0):
        if type(state) != int:
            self.card_open = state
        else:
            self.card_open = not self.card_open
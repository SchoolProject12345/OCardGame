import pygame
from UserInterface.OcgVision.vision_io import KeyRel
from UserInterface.OcgVision.vision_main import State
from Assets.menu_assets import MenuBackgrounds


class JoinMenu(State):
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.is_anchor = False
        self.local_options = ["JoinMenu, GameMenu"]
        super().__init__(screen, self.is_anchor, self.local_options)
        
        self.escp_key = KeyRel(pygame.K_ESCAPE)
        
        self.bg_image = MenuBackgrounds.bg_join_menu_image.convert_alpha()

    def join_menu(self):
        self.screen.blit(self.bg_image, (0, 0))
        
        if self.escp_key.update(pygame.event.get(pygame.KEYUP)):
            self.revert_state()

    def state_manager_hook(self):
        if self.local_state == self.local_options[0]:
            self.join_menu()

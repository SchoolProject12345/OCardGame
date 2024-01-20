import pygame
from UserInterface.OcgVision.vision_main import State, ImageButton, SelectTextBox
from Assets.menu_assets import TextBoxes, MenuBackgrounds
from UserInterface.ui_settings import SCREEN_CENTER
from Debug.DEV_debug import ValueWatcher


class HostMenu(State):
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.is_anchor = False
        self.local_options = ["HostMenu", "Lobby"]
        super().__init__(screen, self.is_anchor, self.local_options)

        self.bg = MenuBackgrounds.bg_host_menu_image.convert_alpha()
        self.bg_rect = self.bg.get_rect()

        self.textbox_image = TextBoxes.textbox_1_image
        self.textbox_rect = self.textbox_image.get_rect(center=(SCREEN_CENTER))

        self.interactive = SelectTextBox(self.screen, (SCREEN_CENTER), 400, 40, pygame.font.SysFont(
            "arial", 30), (255, 255, 255), text_center="center", border_width=2)

    def host_menu(self):
        self.screen.blit(self.bg, self.bg_rect)
        self.screen.blit(self.textbox_image, self.textbox_rect)
        self.interactive.update(pygame.event.get(eventtype=pygame.KEYDOWN))
        # ValueWatcher(self.screen,self.interactive.text)

    def state_manager_hook(self):
        if self.local_state == self.local_options[0]:
            self.host_menu()

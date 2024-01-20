import pygame
from time import time
from UserInterface.OcgVision.vision_main import State, ImageButton
from UserInterface.OcgVision.vision_io import KeyToggle
from Assets.menu_assets import MenuBackgrounds, MenuButtons, alpha_converter
from UserInterface.ui_settings import SCREEN_CENTER
from Debug.DEV_debug import ValueWatcher


class GameMenu(State):
    def __init__(self, screen):
        self.screen = screen
        self.is_anchor = False
        self.local_options = ["GameMenu"]
        super().__init__(self.screen, self.is_anchor, self.local_options)

        self.bg_game_menu_image = MenuBackgrounds.bg_game_menu_image.convert_alpha()
        self.bg_game_menu_rect = self.bg_game_menu_image.get_rect()

        self.bg_pause_menu_image = MenuBackgrounds.bg_pause_menu_image.convert_alpha()
        self.bg_pause_menu_rect = self.bg_pause_menu_image.get_rect(
            center=SCREEN_CENTER)

        self.is_paused_toggle = KeyToggle(pygame.K_ESCAPE, False)

    def game_menu(self):
        self.screen.blit(self.bg_game_menu_image, self.bg_game_menu_rect)

        if self.is_paused_toggle.update(pygame.key.get_pressed()):
            self.screen.blit(self.bg_pause_menu_image, self.bg_pause_menu_rect)

    def state_manager_hook(self):
        if self.local_state == self.local_options[0]:
            self.game_menu()

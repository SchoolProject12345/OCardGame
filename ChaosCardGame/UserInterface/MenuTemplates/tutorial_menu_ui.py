import pygame
from UserInterface.ui_settings import SCREEN_CENTER
from UserInterface.OcgVision.vision_main import State, ImageButton
from UserInterface.OcgVision.vision_io import KeyRel
from Assets.menu_assets import MenuBackgrounds, MenuButtons, alpha_converter

class TutorialMenu(State):
    def __init__(self, screen):
        self.screen = screen
        self.is_anchor = False
        self.local_options = ["TutorialMenu"]
        super().__init__(self.screen, self.is_anchor, self.local_options)
        self.escp_rel = KeyRel(pygame.K_ESCAPE)

        self.bg_tutorial1_menu_image = MenuBackgrounds.bg_tutorial1_image.convert_alpha()
        self.bg_tutorial1_menu_rect = self.bg_tutorial1_menu_image.get_rect()

        self.bg_tutorial2_menu_image = MenuBackgrounds.bg_tutorial2_image.convert_alpha()
        self.bg_tutorial2_menu_rect = self.bg_tutorial2_menu_image.get_rect()

        self.bg_tutorial3_menu_image = MenuBackgrounds.bg_tutorial3_image.convert_alpha()
        self.bg_tutorial3_menu_rect = self.bg_tutorial3_menu_image.get_rect()

        self.bg_tutorial4_menu_image = MenuBackgrounds.bg_tutorial4_image.convert_alpha()
        self.bg_tutorial4_menu_rect = self.bg_tutorial4_menu_image.get_rect()

        self.bg_tutorial5_menu_image = MenuBackgrounds.bg_tutorial5_image.convert_alpha()
        self.bg_tutorial5_menu_rect = self.bg_tutorial5_menu_image.get_rect()

        self.bg_tutorial6_menu_image = MenuBackgrounds.bg_tutorial6_image.convert_alpha()
        self.bg_tutorial6_menu_rect = self.bg_tutorial6_menu_image.get_rect()

        self.bg_tutorial7_menu_image = MenuBackgrounds.bg_tutorial7_image.convert_alpha()
        self.bg_tutorial7_menu_rect = self.bg_tutorial7_menu_image.get_rect()

        self.bg_tutorial8_menu_image = MenuBackgrounds.bg_tutorial8_image.convert_alpha()
        self.bg_tutorial8_menu_rect = self.bg_tutorial8_menu_image.get_rect()

        self.bg_tutorial9_menu_image = MenuBackgrounds.bg_tutorial9_image.convert_alpha()
        self.bg_tutorial9_menu_rect = self.bg_tutorial9_menu_image.get_rect()
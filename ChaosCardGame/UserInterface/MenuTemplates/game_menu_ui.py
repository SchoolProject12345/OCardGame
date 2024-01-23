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

        # Game Menu
        self.bg_game_menu_image = MenuBackgrounds.bg_game_menu_image.convert_alpha()
        self.bg_game_menu_rect = self.bg_game_menu_image.get_rect()

        self.hand_button = ImageButton(self.screen, True, image=alpha_converter(
            MenuButtons.hand_button_image), position_type="center", position=(0,0))
        self.deck_button = ImageButton(self.screen, True, image=alpha_converter(
            MenuButtons.deck_button_image), position_type="center", position=(0,0))

        # Pause Menu
        self.bg_pause_menu_image = MenuBackgrounds.bg_pause_menu_image.convert_alpha()
        self.bg_pause_menu_rect = self.bg_pause_menu_image.get_rect(
            center=SCREEN_CENTER)
        
        self.back_button = ImageButton(self.screen, True, image=alpha_converter(
            MenuButtons.back_button_image), position_type="center",position=(SCREEN_CENTER[0], 294))
        self.settings_button = ImageButton(self.screen, True, image=alpha_converter(
            MenuButtons.settings_button_image), position_type="center",position=(SCREEN_CENTER[0], 392))
        self.surrender_button = ImageButton(self.screen, True, image=alpha_converter(
            MenuButtons.surrender_button_image), postion_type="center",position=(SCREEN_CENTER[0], 490))

        self.is_paused_toggle = KeyToggle(pygame.K_ESCAPE, False)

    def game_menu(self):
        self.screen.blit(self.bg_game_menu_image, self.bg_game_menu_rect)

        if self.is_paused_toggle.update(pygame.key.get_pressed()):
            self.screen.blit(self.bg_pause_menu_image, self.bg_pause_menu_rect)
            self.back_button.render()
            self.settings_button.render()
            self.surrender_button.render()
            self.hand_button.render()
            self.deck_button.render()

            if self.back_button.answer():
                self.is_paused_toggle.toggle()
            elif self.settings_button.answer():
                pass
            elif self.surrender_button.answer():
                self.is_paused_toggle.toggle() # Needs to reset the game
                self.revert_state(2)

    def state_manager_hook(self):
        if self.local_state == self.local_options[0]:
            self.game_menu()

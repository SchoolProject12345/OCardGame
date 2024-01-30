import pygame
from UserInterface.OcgVision.vision_io import KeyRel
from UserInterface.OcgVision.vision_main import State, ImageButton
from Assets.menu_assets import MenuBackgrounds, MenuButtons, alpha_converter
from UserInterface.ui_settings import SCREEN_CENTER
from Debug.DEV_debug import ValueWatcher
 

class GameMenu(State):
    def __init__(self, screen):
        self.screen = screen
        self.is_anchor = False
        self.local_options = ["GameMenu"]
        super().__init__(self.screen, self.is_anchor, self.local_options)
        self.escp_rel = KeyRel(pygame.K_ESCAPE)
        self.is_paused = False

        # Game Menu
        self.bg_game_menu_image = MenuBackgrounds.bg_game_menu_image.convert_alpha()
        self.bg_game_menu_rect = self.bg_game_menu_image.get_rect()

        self.hand_button = ImageButton(self.screen, True, image=alpha_converter(
            MenuButtons.hand_button_image), position_type="topleft", position=(287, 706))
        self.deck_button = ImageButton(self.screen, True, image=alpha_converter(
            MenuButtons.deck_button_image), position_type="topleft", position=(815, 706))

        # Pause Menu
        self.bg_pause_menu_image = MenuBackgrounds.bg_pause_menu_image.convert_alpha()
        self.bg_pause_menu_rect = self.bg_pause_menu_image.get_rect(
            center=SCREEN_CENTER)

        self.back_button = ImageButton(self.screen, True, image=alpha_converter(
            MenuButtons.back_button_image), position_type="center", position=(SCREEN_CENTER[0], 294))
        self.settings_button = ImageButton(self.screen, True, image=alpha_converter(
            MenuButtons.settings_button_image), position_type="center", position=(SCREEN_CENTER[0], 392))
        self.surrender_button = ImageButton(self.screen, True, image=alpha_converter(
            MenuButtons.surrender_button_image), postion_type="center", position=(SCREEN_CENTER[0], 490))

    def is_paused_toggle(self):
        self.is_paused = not self.is_paused

    def game_menu(self):
        self.screen.blit(self.bg_game_menu_image, self.bg_game_menu_rect)

        self.hand_button.render()
        self.deck_button.render()

        if self.escp_rel.update(pygame.event.get(pygame.KEYUP)):
            self.is_paused_toggle()

        if self.is_paused:
            self.screen.blit(self.bg_pause_menu_image, self.bg_pause_menu_rect)
            self.back_button.render()
            self.settings_button.render()
            self.surrender_button.render()
            if self.back_button.answer():
                self.is_paused_toggle()
            elif self.settings_button.answer():
                pass
            elif self.surrender_button.answer():
                self.is_paused_toggle()  # Needs to reset the game
                self.revert_state(2)

    def state_manager_hook(self):
        if self.local_state == self.local_options[0]:
            self.game_menu()

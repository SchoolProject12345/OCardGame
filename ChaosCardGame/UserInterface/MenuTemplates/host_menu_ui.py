import pygame
from UserInterface.OcgVision.vision_main import State, ImageButton
from Assets.menu_assets import MenuBackgrounds, MenuButtons, alpha_converter
from UserInterface.MenuTemplates.game_menu_ui import GameMenu
from UserInterface.ui_settings import SCREEN_CENTER

class HostMenu(State):
    def __init__(self, screen):
        self.screen = screen
        self.is_anchor = False
        self.local_options = ["HostMenu", "GameMenu"]
        super().__init__(self.screen, self.is_anchor, self.local_options)

        self.bg_host_menu_image = MenuBackgrounds.bg_host_menu_image.convert_alpha()
        self.bg_host_menu_rect = self.bg_host_menu_image.get_rect()

        self.hostmenu_host_button = ImageButton(self.screen, True, image=alpha_converter(
            MenuButtons.host_button_image), position_type="center", position=(SCREEN_CENTER[0], SCREEN_CENTER[1] + 202))
        
        self.hostmenu_exit_button = ImageButton(self.screen, True, image=alpha_converter(
            MenuButtons.exit_button_image), position_type="center", position=(SCREEN_CENTER[0], SCREEN_CENTER[1]+302))

        # Options
        self.game_menu = GameMenu(self.screen)

    def host_menu(self):
        self.screen.blit(self.bg_host_menu_image, self.bg_host_menu_rect)
        self.hostmenu_host_button.render()
        self.hostmenu_exit_button.render()

        if self.hostmenu_host_button.answer():
            self.change_state("GameMenu")
        elif self.hostmenu_exit_button.answer() or pygame.key.get_pressed()[pygame.K_ESCAPE]:
            self.revert_state(2)

    def state_manager_hook(self):
        if self.local_state == self.local_options[0]:
            self.host_menu()
        elif self.local_state == self.local_options[1]:
            self.game_menu.state_manager()

import pygame
from UserInterface.ui_settings import SCREEN_CENTER
from UserInterface.OcgVision.vision_main import State, ImageButton
from UserInterface.OcgVision.vision_io import KeyRel
from UserInterface.MenuTemplates.join_menu_ui import JoinMenu
from UserInterface.MenuTemplates.host_menu_ui import HostMenu
from Assets.menu_assets import MenuBackgrounds, MenuButtons, alpha_converter
 
class PlayMenu(State):
    def __init__(self, screen):
        self.screen = screen
        self.is_anchor = False
        self.local_options = ["PlayMenu", "HostMenu", "JoinMenu"]
        super().__init__(self.screen, self.is_anchor, self.local_options)
        self.escp_rel = KeyRel(pygame.K_ESCAPE)

        self.bg_play_menu_image = MenuBackgrounds.bg_play_menu_image.convert_alpha()
        self.bg_play_menu_rect = self.bg_play_menu_image.get_rect()

        self.join_button = ImageButton(self.screen, True, image=alpha_converter(
            MenuButtons.join_button_image), position_type="center", position=(SCREEN_CENTER[0], SCREEN_CENTER[1] + 102))

        self.playmenu_host_button = ImageButton(self.screen, True, image=alpha_converter(
            MenuButtons.host_button_image), position_type="center", position=(SCREEN_CENTER[0], SCREEN_CENTER[1] + 2))

        self.playmenu_exit_button = ImageButton(self.screen, True, image=alpha_converter(
            MenuButtons.exit_button_image), position_type="center", position=(SCREEN_CENTER[0], SCREEN_CENTER[1]+302))

        # Options
        self.host_menu = HostMenu(self.screen)
        self.join_menu = JoinMenu(self.screen)

    def play_menu(self):
        self.screen.blit(self.bg_play_menu_image, self.bg_play_menu_rect)
        self.playmenu_host_button.render()
        self.join_button.render()
        self.playmenu_exit_button.render()

        if self.playmenu_host_button.answer():
            self.change_state("HostMenu")
        elif self.join_button.answer():
            self.change_state("JoinMenu")
        elif self.playmenu_exit_button.answer() or self.escp_rel.update(pygame.event.get(pygame.KEYUP)):
            self.revert_state()

    def state_manager_hook(self):
        if self.local_state == self.local_options[0]:
            self.play_menu()
        elif self.local_state == self.local_options[1]:
            self.host_menu.state_manager_hook()
        elif self.local_state == self.local_options[2]:
            self.join_menu.state_manager_hook()

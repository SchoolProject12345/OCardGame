import pygame
from UserInterface.ui_settings import SCREEN_CENTER
from UserInterface.OcgVision.vision_main import State, ImageButton
from UserInterface.OcgVision.vision_io import KeyRel
from UserInterface.MenuStates.join_menu_ui import JoinMenu
from UserInterface.MenuStates.host_menu_ui import HostMenu
from Assets.menu_assets import MenuBackgrounds, MenuButtons, alpha_converter
 
class PlayMenu(State):
    def __init__(self, screen):
        self.screen = screen
        self.is_anchor = False
        self.local_options = ["PlayMenu", "HostMenu", "JoinMenu"]
        super().__init__(self.screen, self.is_anchor, self.local_options)
        self.escp_rel = KeyRel(pygame.K_ESCAPE)

        self.bg_play_menu_image = MenuBackgrounds.bg_assets["play_menu_empty"]["processed_img"].convert_alpha()
        self.bg_play_menu_rect = self.bg_play_menu_image.get_rect()

        self.playmenu_join_button = ImageButton(
            self.screen,
            True,
            image=alpha_converter(MenuButtons.button_assets["Join"]["processed_img"]),
            position_type="center",
            position=(SCREEN_CENTER[0], SCREEN_CENTER[1] + 102)
            )

        self.playmenu_host_button = ImageButton(
            self.screen,
            True,
            image=alpha_converter(MenuButtons.button_assets["Host"]["processed_img"]),
            position_type="center",
            position=(SCREEN_CENTER[0], SCREEN_CENTER[1] + 2)
            )

        self.playmenu_exit_button = ImageButton(
            self.screen,
            True,
            image=alpha_converter(MenuButtons.button_assets["Exit"]["processed_img"]),
            position_type="center",
            position=(SCREEN_CENTER[0], SCREEN_CENTER[1]+302)
            )

    def play_menu(self):
        self.screen.blit(self.bg_play_menu_image, self.bg_play_menu_rect)
        self.playmenu_host_button.render()
        self.playmenu_join_button.render()
        self.playmenu_exit_button.render()

        if self.playmenu_host_button.answer():
            self.change_state("HostMenu")
        elif self.playmenu_join_button.answer():
            self.change_state("JoinMenu")
        elif self.playmenu_exit_button.answer() or self.escp_rel.update(pygame.event.get(pygame.KEYUP)):
            self.revert_state()

    def state_manager_hook(self,app):
        if len(State.state_tree) >= 3:
            if State.state_tree[2] == self.local_options[1]:
                app.menu_instances["host_menu"].state_manager(app)
            elif State.state_tree[2] == self.local_options[2]:
                app.menu_instances["join_menu"].state_manager(app)
        elif State.state_tree[1] == self.local_options[0]:
            self.play_menu()

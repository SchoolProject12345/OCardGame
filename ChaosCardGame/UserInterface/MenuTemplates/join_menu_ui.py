import pygame
from utility import cwd_path
import os
from UserInterface.OcgVision.vision_io import KeyRel
from UserInterface.OcgVision.vision_main import State, ImageButton, SelectTextBox
from Assets.menu_assets import MenuBackgrounds, MenuButtons, TextBoxes, alpha_converter
from UserInterface.MenuTemplates.game_menu_ui import GameMenu
from UserInterface.ui_settings import SCREEN_CENTER


class JoinMenu(State):
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.is_anchor = False
        self.local_options = ["JoinMenu", "GameMenu"]
        super().__init__(screen, self.is_anchor, self.local_options)
        self.ger_font_path = os.path.join(
            cwd_path, "Assets", "Fonts", "GermaniaOne-Regular.ttf")
        self.escp_key = KeyRel(pygame.K_ESCAPE)
        
        self.bg_join_menu_image = MenuBackgrounds.bg_join_menu_image.convert_alpha()
        self.bg_join_menu_rect = self.bg_join_menu_image.get_rect()

        self.tb_image = TextBoxes.textbox_1_image.convert_alpha()
        self.ipaddress_tb_rect = self.tb_image.get_rect(topleft=(438, 332))
        self.joinmenu_username_tb_rect = self.tb_image.get_rect(topleft=(438,429))

        self.tb_ipaddress = SelectTextBox(self.screen, SCREEN_CENTER, 400, 50, pygame.font.Font(
            self.ger_font_path, 53), (97,97,97), (255,255,255), position_type="center", text_center="center", default_text="IP Address")
        self.joinmenu_tb_username = SelectTextBox(self.screen, (SCREEN_CENTER[0], SCREEN_CENTER[1]+97), 400, 50, pygame.font.Font(
            self.ger_font_path, 53), (97, 97, 97), (255, 255, 255), position_type="center", text_center="center", default_text="Username")
        
        self.joinmenu_join_button = ImageButton(self.screen, True, image=alpha_converter(
            MenuButtons.join_button_image), position_type="center",position=(SCREEN_CENTER[0], SCREEN_CENTER[1] + 202))
        self.joinmenu_exit_button = ImageButton(self.screen, True, image=alpha_converter(
            MenuButtons.exit_button_image), position_type="center", position=(SCREEN_CENTER[0], SCREEN_CENTER[1]+302))

        # Options
        self.game_menu = GameMenu(self.screen)

    def join_menu(self):
        self.screen.blit(self.bg_join_menu_image, self.bg_join_menu_rect)
        self.screen.blit(self.tb_image, self.ipaddress_tb_rect)
        self.screen.blit(self.tb_image, self.joinmenu_username_tb_rect)
        self.joinmenu_join_button.render()
        self.joinmenu_exit_button.render()
        
        keys = pygame.event.get(pygame.KEYDOWN)
        self.room_text = self.tb_ipaddress.render(keys)
        self.username_text = self.joinmenu_tb_username.render(keys)

        if self.joinmenu_join_button.answer():
            self.change_state("GameMenu") # Needs GameState file to be fixed
        if self.joinmenu_exit_button.answer() or self.escp_key.update(pygame.event.get(pygame.KEYUP)):
            self.revert_state(1)

    def state_manager_hook(self):
        if self.local_state == self.local_options[0]:
            self.join_menu()
        if self.local_state == self.local_options[1]:
            self.game_menu.state_manager()

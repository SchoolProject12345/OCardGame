import os
import pygame
import Network.server as server
from random import randint
from Assets.menu_assets import MenuBackgrounds, MenuButtons, alpha_converter
from UserInterface.MenuStates.game_menu_ui import GameMenu
from UserInterface.OcgVision.vision_io import KeyRel
from UserInterface.OcgVision.vision_main import ImageButton, State, TextBox
from UserInterface.ui_settings import SCREEN_CENTER
from utility import cwd_path

class LobbyMenu(State):
    def __init__(self,screen : pygame.surface.Surface):
        self.screen = screen
        self.is_anchor = False
        self.local_options = ["LobbyMenu", "GameMenu"]
        super().__init__(screen, self.is_anchor, self.local_options)
        self.ger_font_path = os.path.join(
            cwd_path, "Assets", "Fonts", "GermaniaOne-Regular.ttf")

        self.bg_lobby_image = MenuBackgrounds.bg_lobby_images[randint(0,4)].convert_alpha()
        self.bg_lobby_rect = self.bg_lobby_image.get_rect()

        self.username_text = TextBox(self.screen, (611, 356), 123, 41, pygame.font.Font(
            self.ger_font_path, 40), (255, 255, 255), position_type="topleft", text_center="center", text="")
        self.ipaddress_text = TextBox(self.screen, (611, 483), 195, 30, pygame.font.Font(
            self.ger_font_path, 30), (255, 255, 255), position_type="topleft", text_center="center", text="")
        self.roomname_text = TextBox(self.screen, (611, 538), 204, 30, pygame.font.Font(
            self.ger_font_path, 30), (255, 255, 255), position_type="topleft", text_center="center", text="")
        
        self.ready_button = ImageButton(self.screen, True, image=alpha_converter(
            MenuButtons.ready_button_image), position_type="topleft", position=(508, 606))
        
    def lobby_menu(self):
        self.screen.blit(self.bg_lobby_image, self.bg_lobby_rect)

        self.username_text.render("Loading...") # Username goes here - link with network
        self.ipaddress_text.render(server.net.get_ip()) # IP Address goes here - link with network
        self.roomname_text.render("Loading...") # Roomname goes here - link with network

        self.ready_button.render()

        if self.ready_button.answer():
            self.change_state("GameMenu")
        
    def state_manager_hook(self, app):
        if len(State.state_tree) >= 5:
            if State.state_tree[4] == self.local_options[1]:
                app.menu_instances["game_menu"].state_manager(app)
        elif State.state_tree[3] == self.local_options[0]:
            self.lobby_menu()
import os
import pygame
from Network.server import HandlerHandler as handle
from random import randint
from Assets.menu_assets import MenuBackgrounds, MenuButtons, Fonts, alpha_converter
from UserInterface.MenuStates.game_menu_ui import GameMenu
from UserInterface.OcgVision.vision_io import KeyRel
from UserInterface.OcgVision.vision_main import ImageButton, State, TextBox
from UserInterface.ui_settings import SCREEN_CENTER
from utility import cwd_path, get_setting


class LobbyMenu(State):
    def __init__(self, screen: pygame.surface.Surface):
        self.screen = screen
        self.is_anchor = False
        self.local_options = ["LobbyMenu", "GameMenu"]
        super().__init__(screen, self.is_anchor, self.local_options)

        self.bg_lobby_image = MenuBackgrounds.bg_lobby_images[
            min(handle.get_state()["arena"], 4)
        ].convert_alpha()
        self.bg_lobby_rect = self.bg_lobby_image.get_rect()

        self.hostusername_text = TextBox(self.screen, (611, 301), 123, 41, Fonts.ger_font(
            40), (255, 255, 255), position_type="topleft", text_center="center", text="")
        self.username_text = TextBox(self.screen, (611, 356), 123, 41, Fonts.ger_font(
            40), (255, 255, 255), position_type="topleft", text_center="center", text="")
        self.ipaddress_text = TextBox(self.screen, (611, 483), 195, 30, Fonts.ger_font(
            30), (255, 255, 255), position_type="topleft", text_center="center", text="")
        self.roomname_text = TextBox(self.screen, (611, 538), 204, 30, Fonts.ger_font(
            30), (255, 255, 255), position_type="topleft", text_center="center", text="")

        self.ready_button = ImageButton(self.screen, True, image=alpha_converter(
            MenuButtons.button_assets["Ready"]["img"]), position_type="topleft", position=(508, 606))

        self.roomname_text_content = get_setting("roomname", "Default")
        self.local_is_hosting = get_setting("is_hosting", False)
        # print(self.local_is_hosting)

    def lobby_menu(self):
        self.screen.blit(self.bg_lobby_image, self.bg_lobby_rect)

        if self.local_is_hosting == True:
            self.hostusername_text_content = get_setting("username", "")
            # self.username_text_content
        else:
            # self.hostusername_text_content
            self.username_text_content = get_setting("username", "")

        if self.local_is_hosting:
            self.hostusername_text.render(self.hostusername_text_content)
            # self.username_text.render(self.username_text_content)
        else:
            # self.hostusername_text.render(self.hostusername_text_content)
            self.username_text.render(self.username_text_content)

        self.ipaddress_text.render(handle.ip_address)
        self.roomname_text.render(self.roomname_text_content)

        self.ready_button.render()

        if self.ready_button.answer():
            self.change_state("GameMenu")

    def state_manager_hook(self, app):
        if len(State.state_tree) >= 5:
            if State.state_tree[4] == self.local_options[1]:
                app.menu_instances["game_menu"].state_manager(app)
        elif State.state_tree[3] == self.local_options[0]:
            self.lobby_menu()

import pygame
import os
from Network.server import HandlerHandler as handle, host as host_server
from UserInterface.OcgVision.vision_io import KeyRel
from UserInterface.OcgVision.vision_main import State, ImageButton, SelectTextBox
from Assets.menu_assets import MenuBackgrounds, MenuButtons, TextBoxes, alpha_converter
from UserInterface.MenuStates.game_menu_ui import GameMenu
from UserInterface.ui_settings import SCREEN_CENTER
from utility import cwd_path, search_event


class HostMenu(State):
    def __init__(self, screen):
        self.screen = screen
        self.is_anchor = False
        self.local_options = ["HostMenu", "LobbyMenu"]
        super().__init__(self.screen, self.is_anchor, self.local_options)
        self.ger_font_path = os.path.join(
            cwd_path, "Assets", "Fonts", "GermaniaOne-Regular.ttf")
        self.escp_rel = KeyRel(pygame.K_ESCAPE)

        self.bg_host_menu_image = MenuBackgrounds.bg_assets["host_menu_empty"]["img"].convert_alpha(
        )
        self.bg_host_menu_rect = self.bg_host_menu_image.get_rect()

        # Select Text Boxes
        self.tb_image = TextBoxes.textbox_1_image.convert_alpha()
        self.roomname_tb_rect = self.tb_image.get_rect(topleft=(438, 332))
        self.hostmenu_username_tb_rect = self.tb_image.get_rect(
            topleft=(438, 429))

        self.tb_roomname = SelectTextBox(
            self.screen,
            position=SCREEN_CENTER,
            width=400,
            height=50,
            font=pygame.font.Font(self.ger_font_path, 53),
            default_color=(97, 97, 97),
            color=(255, 255, 255),
            position_type="center",
            text_center="center",
            default_text="Roomname"
        )

        self.hostmenu_tb_username = SelectTextBox(
            self.screen,
            position=(SCREEN_CENTER[0], SCREEN_CENTER[1]+97),
            width=400,
            height=50,
            font=pygame.font.Font(self.ger_font_path, 53),
            default_color=(97, 97, 97),
            color=(255, 255, 255),
            position_type="center",
            text_center="center",
            default_text="Username"
        )

        # Buttons
        self.hostmenu_host_button = ImageButton(
            self.screen,
            True,
            image=alpha_converter(MenuButtons.button_assets["Host"]["img"]),
            position_type="center",
            position=(SCREEN_CENTER[0], SCREEN_CENTER[1] + 202)
        )

        self.hostmenu_exit_button = ImageButton(
            self.screen,
            True,
            image=alpha_converter(MenuButtons.button_assets["Exit"]["img"]),
            position_type="center",
            position=(SCREEN_CENTER[0], SCREEN_CENTER[1]+302)
        )

    def host_menu(self):
        self.screen.blit(self.bg_host_menu_image, self.bg_host_menu_rect)
        self.screen.blit(self.tb_image, self.roomname_tb_rect)
        self.screen.blit(self.tb_image, self.hostmenu_username_tb_rect)
        self.hostmenu_host_button.render()
        self.hostmenu_exit_button.render()

        keys = search_event(super().events, pygame.KEYDOWN)
        self.room_text = self.tb_roomname.render(keys)
        self.username_text = self.hostmenu_tb_username.render(keys)

        if self.hostmenu_host_button.answer():
            self.roomname = self.tb_roomname.text
            self.player_username = self.hostmenu_tb_username.text
            self.change_state("LobbyMenu")
        if self.hostmenu_exit_button.answer() or self.escp_rel.update(search_event(super().events, pygame.KEYUP)):
            self.revert_state()

    def state_manager_hook(self, app):
        if len(State.state_tree) >= 4:
            if State.state_tree[3] == self.local_options[1]:
                app.menu_instances["lobby_menu"].state_manager(app)
        elif State.state_tree[2] == self.local_options[0]:
            self.host_menu()

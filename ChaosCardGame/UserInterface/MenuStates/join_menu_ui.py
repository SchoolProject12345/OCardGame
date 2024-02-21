import os
import pygame
# join might conflict
from Network.server import HandlerHandler as handle, join as join_server
from Assets.menu_assets import MenuBackgrounds, MenuButtons, TextBoxes, alpha_converter
from UserInterface.MenuStates.game_menu_ui import GameMenu
from UserInterface.MenuStates.lobby_menu_ui import LobbyMenu
from UserInterface.OcgVision.vision_io import KeyRel
from UserInterface.OcgVision.vision_main import ImageButton, SelectTextBox, State
from UserInterface.ui_settings import SCREEN_CENTER
from utility import cwd_path, search_event


class JoinMenu(State):
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.is_anchor = False
        self.local_options = ["JoinMenu", "LobbyMenu"]
        super().__init__(screen, self.is_anchor, self.local_options)
        self.ger_font_path = os.path.join(
            cwd_path, "Assets", "Fonts", "GermaniaOne-Regular.ttf")
        self.escp_key = KeyRel(pygame.K_ESCAPE)

        self.bg_join_menu_image = MenuBackgrounds.bg_assets["join_menu_empty"]["img"].convert_alpha(
        )
        self.bg_join_menu_rect = self.bg_join_menu_image.get_rect()

        # Select Text Boxes
        self.tb_image = TextBoxes.textbox_1_image.convert_alpha()
        self.ipaddress_tb_rect = self.tb_image.get_rect(topleft=(438, 332))
        self.joinmenu_username_tb_rect = self.tb_image.get_rect(
            topleft=(438, 429))

        self.tb_ipaddress = SelectTextBox(
            self.screen,
            position=SCREEN_CENTER,
            width=400,
            height=50,
            font=pygame.font.Font(self.ger_font_path, 53),
            default_color=(97, 97, 97),
            color=(255, 255, 255),
            position_type="center",
            text_center="center",
            default_text="IP Address"
        )

        self.joinmenu_tb_username = SelectTextBox(
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
        self.joinmenu_join_button = ImageButton(
            self.screen,
            True,
            image=alpha_converter(MenuButtons.button_assets["Join"]["img"]),
            position_type="center",
            position=(SCREEN_CENTER[0], SCREEN_CENTER[1] + 202)
        )

        self.joinmenu_exit_button = ImageButton(
            self.screen,
            True,
            image=alpha_converter(MenuButtons.button_assets["Exit"]["img"]),
            position_type="center",
            position=(SCREEN_CENTER[0],
                      SCREEN_CENTER[1]+302)
        )

    def join_menu(self):
        self.screen.blit(self.bg_join_menu_image, self.bg_join_menu_rect)
        self.screen.blit(self.tb_image, self.ipaddress_tb_rect)
        self.screen.blit(self.tb_image, self.joinmenu_username_tb_rect)
        self.joinmenu_join_button.render()
        self.joinmenu_exit_button.render()

        keys = search_event(super().events, pygame.KEYDOWN)
        self.room_text = self.tb_ipaddress.render(keys)
        self.username_text = self.joinmenu_tb_username.render(keys)

        if self.joinmenu_join_button.answer():
            self.change_state("GameMenu")  # Needs fixing
            self.player_username = self.joinmenu_tb_username.text
        if self.joinmenu_exit_button.answer() or self.escp_key.update(search_event(super().events, pygame.KEYUP)):
            self.revert_state(1)

    def state_manager_hook(self, app):
        if len(State.state_tree) >= 4:
            if State.state_tree[3] == self.local_options[1]:
                app.menu_instances["lobby_menu"].state_manager(app)
        elif State.state_tree[2] == self.local_options[0]:
            self.join_menu()

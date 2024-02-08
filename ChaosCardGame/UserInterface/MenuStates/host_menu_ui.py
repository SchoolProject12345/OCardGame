import pygame
import os
import Network.network as net
import Network.server as server
from UserInterface.OcgVision.vision_io import KeyRel
from UserInterface.OcgVision.vision_main import State, ImageButton, SelectTextBox
from Assets.menu_assets import MenuBackgrounds, MenuButtons, TextBoxes, alpha_converter
from UserInterface.MenuStates.game_menu_ui import GameMenu
from UserInterface.ui_settings import SCREEN_CENTER
from utility import cwd_path


class HostMenu(State):
    def __init__(self, screen):
        self.screen = screen
        self.is_anchor = False
        self.local_options = ["HostMenu", "LobbyMenu"]
        super().__init__(self.screen, self.is_anchor, self.local_options)
        self.ger_font_path = os.path.join(
            cwd_path, "Assets", "Fonts", "GermaniaOne-Regular.ttf")
        self.escp_rel = KeyRel(pygame.K_ESCAPE)

        self.ipaddress = server.net.get_ip()

        self.bg_host_menu_image = MenuBackgrounds.bg_host_menu_image.convert_alpha()
        self.bg_host_menu_rect = self.bg_host_menu_image.get_rect()

        self.tb_image = TextBoxes.textbox_1_image.convert_alpha()
        self.roomname_tb_rect = self.tb_image.get_rect(topleft=(438, 332))
        self.hostmenu_username_tb_rect = self.tb_image.get_rect(
            topleft=(438, 429))

        self.tb_roomname = SelectTextBox(self.screen, SCREEN_CENTER, 400, 50, pygame.font.Font(
            self.ger_font_path, 53), (97, 97, 97), (255, 255, 255), position_type="center", text_center="center", default_text="Roomname")
        self.hostmenu_tb_username = SelectTextBox(self.screen, (SCREEN_CENTER[0], SCREEN_CENTER[1]+97), 400, 50, pygame.font.Font(
            self.ger_font_path, 53), (97, 97, 97), (255, 255, 255), position_type="center", text_center="center", default_text="Username")

        self.hostmenu_host_button = ImageButton(self.screen, True, image=alpha_converter(
            MenuButtons.host_button_image), position_type="center", position=(SCREEN_CENTER[0], SCREEN_CENTER[1] + 202))
        self.hostmenu_exit_button = ImageButton(self.screen, True, image=alpha_converter(
            MenuButtons.exit_button_image), position_type="center", position=(SCREEN_CENTER[0], SCREEN_CENTER[1]+302))

    def host_menu(self):
        self.screen.blit(self.bg_host_menu_image, self.bg_host_menu_rect)
        self.screen.blit(self.tb_image, self.roomname_tb_rect)
        self.screen.blit(self.tb_image, self.hostmenu_username_tb_rect)
        self.hostmenu_host_button.render()
        self.hostmenu_exit_button.render()

        keys = pygame.event.get(pygame.KEYDOWN)
        self.room_text = self.tb_roomname.render(keys)
        self.username_text = self.hostmenu_tb_username.render(keys)

        if self.hostmenu_host_button.answer():
            self.roomname = self.tb_roomname.text
            self.host_username = self.hostmenu_tb_username.text
            self.change_state("LobbyMenu")
            net.threading.Thread(target=server.host, args=(self.host_username, self.ipaddress), daemon=True).start()

        if self.hostmenu_exit_button.answer() or self.escp_rel.update(pygame.event.get(pygame.KEYUP)):
            self.revert_state()

    def state_manager_hook(self, app):
        if len(State.state_tree) >= 4:
            if State.state_tree[3] == self.local_options[1]:
                app.menu_instances["lobby_menu"].state_manager(app)
        elif State.state_tree[2] == self.local_options[0]:
            self.host_menu()

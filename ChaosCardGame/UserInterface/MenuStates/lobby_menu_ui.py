import os
import pygame
from Network.server import HandlerHandler as handle
import random
from Assets.menu_assets import MenuBackgrounds, MenuButtons, TextBoxes, Fonts, alpha_converter
from UserInterface.MenuStates.game_menu_ui import GameMenu
from UserInterface.OcgVision.vision_io import KeyRel
from UserInterface.OcgVision.vision_main import ImageButton, State, TextBox, SelectTextBox
from UserInterface.ui_settings import SCREEN_CENTER
from utility import cwd_path, get_setting, search_event
import random
import re


class LobbyMenu(State):
    def __init__(self, screen: pygame.surface.Surface):
        self.screen = screen
        self.is_anchor = False
        self.local_options = ["LobbyMenu", "GameMenu"]
        super().__init__(screen, self.is_anchor, self.local_options)

        self.tb_image = TextBoxes.textbox_2_image.convert_alpha()
        self.chat_tb_rect = self.tb_image.get_rect(topleft=(777, 629))
        self.messages = ["Message", "Message", "Message", "Message",
                         "Message", "Message", "Message", "Message", "Message", "Message"]

        self.tips = ["Some cards have passives that help you get more energy per turn. Use those to increase your energy generation!",
                     "Use cards who attack all foes to get the advantage on your opponant, on arenas with many slots.",
                     "An enemy card is too strong? Use an ability to block it, either temporarily or forever!",
                     "Don't forget to use your Ultimate! Commander Ultimates charge with damage dealt by your cards, and can turn a game around!",
                     "Block an opponent slot forever with special abilities, to hinder your opponent's capacity to place cards!",
                     "Not dealing enough damage? Use a spell or an ability to boost your ally's attack power!",
                     "Ayo you found a secret! Don't tell anyone, but this tip has a 1/100 chance to appear. You're lucky!"]

        self.tb_chat = SelectTextBox(
            self.screen,
            position=(802, 643),
            width=351,
            height=35,
            font=Fonts.ger_font(30),
            default_color=(97, 97, 97),
            color=(255, 255, 255),
            position_type="topleft",
            text_center="left",
            default_text="Write Here"
        )

        self.current_arena: int = handle.get_state()["arena"]
        self.bg_lobby_image = MenuBackgrounds.bg_lobby_images[
            min(self.current_arena, 4)
        ].convert_alpha()
        self.bg_lobby_rect = self.bg_lobby_image.get_rect()

        self.host_ready_image = MenuBackgrounds.bg_assets["ready"]["img"]
        self.host_ready_rect = self.host_ready_image.get_rect(
            topleft=(393, 321))
        self.host_unready_image = MenuBackgrounds.bg_assets["unready"]["img"]
        self.host_unready_rect = self.host_unready_image.get_rect(
            topleft=(393, 321))

        self.user_ready_image = MenuBackgrounds.bg_assets["ready"]["img"]
        self.user_ready_rect = self.user_ready_image.get_rect(
            topleft=(395, 375))
        self.user_unready_image = MenuBackgrounds.bg_assets["unready"]["img"]
        self.user_unready_rect = self.user_unready_image.get_rect(
            topleft=(395, 375))

        self.hostusername_text = TextBox(self.screen, (257, 311), 123, 41, Fonts.ger_font(
            40), (255, 255, 255), position_type="topleft", text_center="center", text="")
        self.username_text = TextBox(self.screen, (257, 366), 123, 41, Fonts.ger_font(
            40), (255, 255, 255), position_type="topleft", text_center="center", text="")
        self.ipaddress_text = TextBox(self.screen, (257, 493), 195, 30, Fonts.ger_font(
            30), (255, 255, 255), position_type="topleft", text_center="center", text="")
        self.roomname_text = TextBox(self.screen, (257, 548), 204, 30, Fonts.ger_font(
            30), (255, 255, 255), position_type="topleft", text_center="center", text="")

        self.chat0_text = TextBox(self.screen, (777, 121), 485, 35, Fonts.ger_font(
            20), (255, 255, 255), position_type="topleft", text_center="left", text=self.messages[0])
        self.chat1_text = TextBox(self.screen, (777, 163), 485, 35, Fonts.ger_font(
            20), (255, 255, 255), position_type="topleft", text_center="left", text=self.messages[1])
        self.chat2_text = TextBox(self.screen, (777, 205), 485, 35, Fonts.ger_font(
            20), (255, 255, 255), position_type="topleft", text_center="left", text=self.messages[2])
        self.chat3_text = TextBox(self.screen, (777, 247), 485, 35, Fonts.ger_font(
            20), (255, 255, 255), position_type="topleft", text_center="left", text=self.messages[3])
        self.chat4_text = TextBox(self.screen, (777, 289), 485, 35, Fonts.ger_font(
            20), (255, 255, 255), position_type="topleft", text_center="left", text=self.messages[4])
        self.chat5_text = TextBox(self.screen, (777, 331), 485, 35, Fonts.ger_font(
            20), (255, 255, 255), position_type="topleft", text_center="left", text=self.messages[5])
        self.chat6_text = TextBox(self.screen, (777, 373), 485, 35, Fonts.ger_font(
            20), (255, 255, 255), position_type="topleft", text_center="left", text=self.messages[6])
        self.chat7_text = TextBox(self.screen, (777, 415), 485, 35, Fonts.ger_font(
            20), (255, 255, 255), position_type="topleft", text_center="left", text=self.messages[7])
        self.chat8_text = TextBox(self.screen, (777, 457), 485, 35, Fonts.ger_font(
            20), (255, 255, 255), position_type="topleft", text_center="left", text=self.messages[8])
        self.chat9_text = TextBox(self.screen, (777, 499), 485, 35, Fonts.ger_font(
            20), (255, 255, 255), position_type="topleft", text_center="left", text=self.messages[9])

        self.ready_button = ImageButton(self.screen, True, image=alpha_converter(
            MenuButtons.button_assets["Ready"]["img"]), position_type="topleft", position=(154, 616))

        self.send_button = ImageButton(self.screen, True, image=alpha_converter(
            MenuButtons.button_assets["Send"]["img"]), position_type="topleft", position=(1191, 629))

    def pick_tip(self):
        first_random = random.randint(1, 100)
        if first_random == 1:
            return self.tips[6]
        else:
            second_random = random.randint(0, 5)
            return self.tips[second_random]

    def log_chat(self, _, username: str, message: str, text: str):
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        newtext = ansi_escape.sub('', text)
        print(f"Logging message: {newtext}")
        if len(self.messages) < 10:
            self.messages.append(newtext)
        else:
            self.messages.pop(0)
            self.messages.append(newtext)
        self.chat0_text.text = self.messages[0]
        self.chat1_text.text = self.messages[1]
        self.chat2_text.text = self.messages[2]
        self.chat3_text.text = self.messages[3]
        self.chat4_text.text = self.messages[4]
        self.chat5_text.text = self.messages[5]
        self.chat6_text.text = self.messages[6]
        self.chat7_text.text = self.messages[7]
        self.chat8_text.text = self.messages[8]
        self.chat9_text.text = self.messages[9]

    def lobby_menu(self):
        self.roomname_text_content = get_setting("roomname", "Room")
        self.local_is_hosting = get_setting("is_hosting", False)

        # handle.state is faster than handle.get_state()
        if self.current_arena != handle.state["arena"].value:
            self.current_arena = handle.state["arena"].value
            self.bg_lobby_image = MenuBackgrounds.bg_lobby_images[
                min(self.current_arena, 4)
            ].convert_alpha()
            self.bg_lobby_rect = self.bg_lobby_image.get_rect()

        self.screen.blit(self.bg_lobby_image, self.bg_lobby_rect)

        if self.local_is_hosting == True:
            self.hostusername_text_content = get_setting("username", "User")
            self.username_text_content = handle.get_state()["remote"]["name"]
        else:
            self.hostusername_text_content = handle.get_state()[
                "remote"]["name"]
            self.username_text_content = get_setting("username", "User")

        if self.local_is_hosting:
            self.hostusername_text.render(self.hostusername_text_content)
            self.username_text.render(self.username_text_content)
        else:
            self.hostusername_text.render(self.hostusername_text_content)
            self.username_text.render(self.username_text_content)

        self.ipaddress_text.render(handle.ip_address)
        self.roomname_text.render(self.roomname_text_content)
        self.chat0_text.render(self.messages[0])
        self.chat1_text.render(self.messages[1])
        self.chat2_text.render(self.messages[2])
        self.chat3_text.render(self.messages[3])
        self.chat4_text.render(self.messages[4])
        self.chat5_text.render(self.messages[5])
        self.chat6_text.render(self.messages[6])
        self.chat7_text.render(self.messages[7])
        self.chat8_text.render(self.messages[8])
        self.chat9_text.render(self.messages[9])

        self.ready_button.render()
        self.send_button.render()

        if self.ready_button.answer() and not handle.ready:
            handle.run_action("ready")
        if self.send_button.answer():
            handle.run_action(f"chat|{self.tb_chat.text}")
            self.tb_chat.text = ""

        if self.local_is_hosting == True:
            if handle.ready == True:
                self.screen.blit(self.host_ready_image, self.host_ready_rect)
            elif handle.ready == False:
                self.screen.blit(self.host_unready_image,
                                 self.host_unready_rect)
            if handle.remote_ready == True:
                self.screen.blit(self.user_ready_image, self.user_ready_rect)
            elif handle.remote_ready == False:
                self.screen.blit(self.user_unready_image,
                                 self.user_unready_rect)
        elif self.local_is_hosting == False:
            if handle.remote_ready == True:
                self.screen.blit(self.host_ready_image, self.host_ready_rect)
            elif handle.remote_ready == False:
                self.screen.blit(self.host_unready_image,
                                 self.host_unready_rect)
            if handle.ready == True:
                self.screen.blit(self.user_ready_image, self.user_ready_rect)
            elif handle.ready == False:
                self.screen.blit(self.user_unready_image,
                                 self.user_unready_rect)

        self.screen.blit(self.tb_image, self.chat_tb_rect)

        handle.add_log_player(self.log_chat, head="chat")

        keys = search_event(super().events, pygame.KEYDOWN)
        self.room_text = self.tb_chat.render(keys)

        if handle.ready == True and handle.remote_ready == True:
            self.change_state("GameMenu")

    def state_manager_hook(self, app):
        if len(State.state_tree) >= 5:
            if State.state_tree[4] == self.local_options[1]:
                app.menu_instances["game_menu"].state_manager(app)
        elif State.state_tree[3] == self.local_options[0]:
            self.lobby_menu()

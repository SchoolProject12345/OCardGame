import pygame
from utility import cwd_path
import os
from UserInterface.OcgVision.vision_io import KeyRel
from UserInterface.OcgVision.vision_main import State, ImageButton, DualBarVerti, TextBox, coord_grid, ImageToggle
from Assets.menu_assets import MenuBackgrounds, MenuButtons, MenuToggles, alpha_converter
from UserInterface.ui_settings import SCREEN_CENTER


class GameMenu(State):
    def __init__(self, screen):
        self.screen = screen
        self.is_anchor = False
        self.local_options = ["GameMenu"]
        super().__init__(self.screen, self.is_anchor, self.local_options)
        self.escp_rel = KeyRel(pygame.K_ESCAPE)
        self.is_paused = False
        self.is_decked = False
        self.is_handed = False
        self.is_insettings = False

        self.ger_font_path = os.path.join(
            cwd_path, "Assets", "Fonts", "GermaniaOne-Regular.ttf")

        self.player_max_energy = 5
        self.player_health = 500
        self.player_energy = 4

        self.enemy_max_energy = 5
        self.enemy_health = 250
        self.enemy_energy = 2

        # Game Menu
        self.bg_game_menu_image = MenuBackgrounds.bg_game_menu_image.convert_alpha()
        self.bg_game_menu_rect = self.bg_game_menu_image.get_rect(
            topleft=(0, 0))

        self.hand_button = ImageButton(self.screen, True, image=alpha_converter(
            MenuButtons.hand_button_image), position_type="topleft", position=(296, 706))
        self.deck_button = ImageButton(self.screen, True, image=alpha_converter(
            MenuButtons.deck_button_image), position_type="topleft", position=(824, 706))

        self.player_health_bar = DualBarVerti(self.screen, position=(566, 706), position_type="topleft", width=96, height=52,
                                            color_bg=pygame.color.Color(220, 220, 220), color_fg=pygame.color.Color(255, 122, 122), max_value=600)
        self.player_energy_bar = DualBarVerti(self.screen, position=(683, 706), position_type="topleft", width=96, height=52,
                                            color_bg=pygame.color.Color(220, 220, 220), color_fg=pygame.color.Color(122, 215, 255), max_value=self.player_max_energy)
        self.enemy_health_bar = DualBarVerti(self.screen, position=(566, 0), position_type="topleft", width=96, height=52,
                                            color_bg=pygame.color.Color(220, 220, 220), color_fg=pygame.color.Color(255, 122, 122), max_value=600)
        self.enemy_energy_bar = DualBarVerti(self.screen, position=(683, 0), position_type="topleft", width=96, height=52,
                                            color_bg=pygame.color.Color(220, 220, 220), color_fg=pygame.color.Color(122, 215, 255), max_value=self.enemy_max_energy)
        self.player_health_bar_text = TextBox(self.screen, (566, 706), 96, 52, pygame.font.Font(
            self.ger_font_path, 30), (101, 101, 101), position_type="topleft", text_center="center", text="")
        self.player_energy_bar_text = TextBox(self.screen, (683, 706), 96, 52, pygame.font.Font(
            self.ger_font_path, 30), (101, 101, 101), position_type="topleft", text_center="center", text="")
        self.enemy_health_bar_text = TextBox(self.screen, (566, 0), 96, 52, pygame.font.Font(
            self.ger_font_path, 30), (101, 101, 101), position_type="topleft", text_center="center", text="")
        self.enemy_energy_bar_text = TextBox(self.screen, (683, 0), 96, 52, pygame.font.Font(
            self.ger_font_path, 30), (101, 101, 101), position_type="topleft", text_center="center", text="")

        self.player_username_text = TextBox(self.screen, (72, 726), 96, 52, pygame.font.Font(
            self.ger_font_path, 18), (255, 255, 255), position_type="topleft", text_center="center", text="")

        # Pause Menu
        self.bg_pause_menu_image = MenuBackgrounds.bg_pause_menu_image.convert_alpha()
        self.bg_pause_menu_rect = self.bg_pause_menu_image.get_rect(
            center=SCREEN_CENTER)
        self.pauseback_button = ImageButton(self.screen, True, image=alpha_converter(
            MenuButtons.back_button_image), position_type="center", position=(SCREEN_CENTER[0], 294))
        self.settings_button = ImageButton(self.screen, True, image=alpha_converter(
            MenuButtons.settings_button_image), position_type="center", position=(SCREEN_CENTER[0], 392))
        self.surrender_button = ImageButton(self.screen, True, image=alpha_converter(
            MenuButtons.surrender_button_image), postion_type="center", position=(SCREEN_CENTER[0], 490))

        # Deck Menu
        self.bg_deck_menu_image = MenuBackgrounds.bg_deck_menu_image.convert_alpha()
        self.bg_deck_menu_rect = self.bg_deck_menu_image.get_rect(
            center=SCREEN_CENTER)
        self.deckback_button = ImageButton(self.screen, True, image=alpha_converter(
            MenuButtons.back_button_image), position_type="center", position=(SCREEN_CENTER[0], 555))

        # Hand Menu
        self.bg_hand_menu_image = MenuBackgrounds.bg_hand_menu_image.convert_alpha()
        self.bg_hand_menu_rect = self.bg_hand_menu_image.get_rect(
            center=SCREEN_CENTER)
        self.handback_button = ImageButton(self.screen, True, image=alpha_converter(
            MenuButtons.back_button_image), position_type="center", position=(SCREEN_CENTER[0], 555))

        self.coords = coord_grid(SCREEN_CENTER, "center", (300, 300), (2, 2))

        # Settings menu
        self.bg_settings_menu_image = MenuBackgrounds.bg_settings_menu_image.convert_alpha()
        self.bg_settings_menu_rect = self.bg_settings_menu_image.get_rect(
            center=SCREEN_CENTER)
        self.musicmute_toggle = ImageToggle(self.screen, True, is_toggled=False, image=alpha_converter(
            MenuToggles.mute_toggle_image) ,position_type="topleft",position_type_T="topleft", position=(637,288), position_T=(637,288))
        self.sfxmute_toggle = ImageToggle(self.screen, True, is_toggled=False, image=alpha_converter(
            MenuToggles.mute_toggle_image), position_type="topleft", position=(637,370))
        self.settingsback_button = ImageButton(self.screen, True, image=alpha_converter(
            MenuButtons.back_button_image), position_type="topleft", position=(571,519))

    def is_paused_toggle(self):
        self.is_paused = not self.is_paused
    def is_decked_toggle(self):
        self.is_decked = not self.is_decked
    def is_handed_toggle(self):
        self.is_handed = not self.is_handed
    def is_insettings_toggle(self):
        self.is_insettings = not self.is_insettings

    def game_menu(self):
        self.screen.blit(self.bg_game_menu_image, self.bg_game_menu_rect)

        self.player_health_bar.render(self.player_health, False)
        self.player_energy_bar.render(self.player_energy, False)
        self.enemy_health_bar.render(self.enemy_health, True)
        self.enemy_energy_bar.render(self.enemy_energy, True)

        self.player_health_bar_text.render(str(self.player_health))
        self.player_energy_bar_text.render(str(self.player_energy))
        self.enemy_health_bar_text.render(str(self.enemy_health))
        self.enemy_energy_bar_text.render(str(self.enemy_energy))

        for coord in self.coords:
            pygame.draw.circle(self.screen, (255, 255, 255), coord, 10)

        #self.player_username_text.render(str(self.player_username)) # Need to import player_username from host_menu and join_menu

        self.deck_button.render()
        if self.deck_button.answer():
            self.is_decked_toggle()
            self.is_handed = False
            self.is_paused = False
            self.is_insettings = False
        if self.is_decked:
            self.screen.blit(self.bg_deck_menu_image, self.bg_deck_menu_rect)
            self.deckback_button.render()
            if self.deckback_button.answer() or self.escp_rel.update(pygame.event.get(pygame.KEYUP)):
                self.is_decked_toggle()

        self.hand_button.render()
        if self.hand_button.answer():
            self.is_handed_toggle()
            self.is_decked = False
            self.is_paused = False
            self.is_insettings = False
        if self.is_handed:
            self.screen.blit(self.bg_hand_menu_image, self.bg_hand_menu_rect)
            self.handback_button.render()
            if self.handback_button.answer() or self.escp_rel.update(pygame.event.get(pygame.KEYUP)):
                self.is_handed_toggle()

        if self.escp_rel.update(pygame.event.get(pygame.KEYUP)):
            self.is_paused_toggle()
            self.is_handed = False
            self.is_decked = False
            self.is_insettings = False
        if self.is_paused:
            self.screen.blit(self.bg_pause_menu_image, self.bg_pause_menu_rect)
            self.pauseback_button.render()
            self.settings_button.render()
            self.surrender_button.render()
            if self.pauseback_button.answer() or self.escp_rel.update(pygame.event.get(pygame.KEYUP)):
                self.is_paused_toggle()
                
            elif self.settings_button.answer():
                self.is_insettings_toggle()
                self.is_handed = False
                self.is_decked = False
                self.is_paused = False
            elif self.surrender_button.answer():
                self.is_paused_toggle()
                self.revert_state(2)

        if self.is_insettings:
            self.screen.blit(self.bg_settings_menu_image, self.bg_settings_menu_rect)
            self.musicmute_toggle.render()
            self.sfxmute_toggle.render()
            self.settingsback_button.render()

            if self.musicmute_toggle.answer(): # A toi de remplir Erik
                print(f"{self.musicmute_toggle.call_back} callback")
            if self.sfxmute_toggle.answer():
                pass


    def state_manager_hook(self, app):
        if len(State.state_tree) >= 6:
            raise ValueError("Bro what?")
        elif State.state_tree[4] == self.local_options[0]:
            self.game_menu()

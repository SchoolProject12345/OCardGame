import pygame
from utility import cwd_path
import os
from UserInterface.OcgVision.vision_io import KeyRel
from UserInterface.OcgVision.vision_main import State, ImageButton, DualBarHori, DualBarVerti, TextBox
from Assets.menu_assets import MenuBackgrounds, MenuButtons, alpha_converter
from UserInterface.ui_settings import SCREEN_CENTER
from Debug.DEV_debug import ValueWatcher


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
        self.bg_game_menu_rect = self.bg_game_menu_image.get_rect()

        self.hand_button = ImageButton(self.screen, True, image=alpha_converter(
            MenuButtons.hand_button_image), position_type="topleft", position=(287, 706))
        self.deck_button = ImageButton(self.screen, True, image=alpha_converter(
            MenuButtons.deck_button_image), position_type="topleft", position=(815, 706))

        self.player_health_bar = DualBarVerti(self.screen, position=(557, 706),position_type="topleft", width=96, height=52,
            color_bg=pygame.color.Color(220, 220, 220), color_fg=pygame.color.Color(255, 122, 122), max_value=600)
        self.player_energy_bar = DualBarVerti(self.screen, position=(674, 706),position_type="topleft", width=96, height=52,
            color_bg=pygame.color.Color(220, 220, 220), color_fg=pygame.color.Color(122, 215, 255),max_value=self.player_max_energy)
        self.enemy_health_bar = DualBarVerti(self.screen, position=(557, 0),position_type="topleft", width=96, height=52,
            color_bg=pygame.color.Color(220, 220, 220), color_fg=pygame.color.Color(255, 122, 122), max_value=600)
        self.enemy_energy_bar = DualBarVerti(self.screen, position=(674, 0),position_type="topleft", width=96, height=52,
            color_bg=pygame.color.Color(220, 220, 220), color_fg=pygame.color.Color(122, 215, 255),max_value=self.enemy_max_energy)

        self.player_health_bar_text = TextBox(self.screen, (557, 706), 400, 50, pygame.font.Font(
            self.ger_font_path, 30), (255, 255, 255), position_type="topleft", text_center="left",text="")
        self.player_energy_bar_text = TextBox(self.screen, (674, 706), 400, 50, pygame.font.Font(
            self.ger_font_path, 30), (255, 255, 255), position_type="topleft", text_center="left",text="")
        self.enemy_health_bar_text = TextBox(self.screen, (557, 0), 400, 50, pygame.font.Font(
            self.ger_font_path, 30), (255, 255, 255), position_type="topleft", text_center="left",text="")
        self.enemy_energy_bar_text = TextBox(self.screen, (674, 0), 400, 50, pygame.font.Font(
            self.ger_font_path, 30), (255, 255, 255), position_type="topleft", text_center="left",text="")


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
            MenuButtons.back_button_image), position_type="center",position=(SCREEN_CENTER[0], 555))
        

        # Hand Menu
        self.bg_hand_menu_image = MenuBackgrounds.bg_hand_menu_image.convert_alpha()
        self.bg_hand_menu_rect = self.bg_hand_menu_image.get_rect(
            center=SCREEN_CENTER)
        
        self.handback_button = ImageButton(self.screen,True,image=alpha_converter(
            MenuButtons.back_button_image), position_type="center", position=(SCREEN_CENTER[0], 555))

    def is_paused_toggle(self):
        self.is_paused = not self.is_paused

    def is_decked_toggle(self):
        self.is_decked = not self.is_decked

    def is_handed_toggle(self):
        self.is_handed = not self.is_handed


    def game_menu(self):
        self.screen.blit(self.bg_game_menu_image, self.bg_game_menu_rect)

        self.player_health_bar.render(self.player_health, False)
        self.player_energy_bar.render(self.player_energy, False)
        self.enemy_health_bar.render(self.enemy_health, True)
        self.enemy_energy_bar.render(self.enemy_energy, True)
        
        self.player_health_bar_text.render(str(self.player_health) + "HP")
        self.player_energy_bar_text.render(str(self.player_energy) + "NRG")
        self.enemy_health_bar_text.render(str(self.enemy_health) + "HP")
        self.enemy_energy_bar_text.render(str(self.enemy_energy) + "NRG")

        self.deck_button.render()
        if self.deck_button.answer():
            self.is_decked_toggle()
        if self.is_decked:
            self.screen.blit(self.bg_deck_menu_image, self.bg_deck_menu_rect)
            self.deckback_button.render()
            if self.deckback_button.answer():
                self.is_decked_toggle()


        self.hand_button.render()
        if self.hand_button.answer():
            self.is_handed_toggle()
        if self.is_handed:
            self.screen.blit(self.bg_hand_menu_image, self.bg_hand_menu_rect)
            self.handback_button.render()
            if self.handback_button.answer():
                self.is_handed_toggle()


        if self.escp_rel.update(pygame.event.get(pygame.KEYUP)):
            self.is_paused_toggle()

        if self.is_paused:
            self.screen.blit(self.bg_pause_menu_image, self.bg_pause_menu_rect)          
            self.pauseback_button.render()
            self.settings_button.render()
            self.surrender_button.render()
            if self.pauseback_button.answer():
                self.is_paused_toggle()
            elif self.settings_button.answer():
                pass
            elif self.surrender_button.answer():
                self.revert_state()
                self.is_paused_toggle()

    def state_manager_hook(self):
        if self.local_state == self.local_options[0]:
            self.game_menu()

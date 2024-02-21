import pygame
from UserInterface.ui_settings import SCREEN_CENTER
from UserInterface.OcgVision.vision_main import State, ImageButton
from UserInterface.MenuStates.play_menu_ui import PlayMenu
from UserInterface.MenuStates.credits_menu_ui import CreditsMenu
from UserInterface.MenuStates.cards_menu_ui import CardsMenu
from UserInterface.MenuStates.tutorial_menu_ui import TutorialMenu
from UserInterface.MenuStates.lore_menu_ui import LoreMenu
from Assets.menu_assets import MenuBackgrounds, MenuButtons, alpha_converter
from SfxEngine.SoundEngine import sound_handle
import os
from UserInterface.card_handler import CardHolder


class MainMenu(State):
    def __init__(self, screen):
        super().__init__(
            screen,
            True,
            [
                "MainMenu",
                "PlayMenu",
                "CardsMenu",
                "CreditsMenu",
                "TutorialMenu",
                "LoreMenu",
            ],
        )

        self.bg_main_menu_image = MenuBackgrounds.bg_assets["main_menu_empty"][
            "img"
        ].convert_alpha()
        self.bg_main_menu_rect = self.bg_main_menu_image.get_rect(
            topleft=(0, 0))

        self.quit_event = pygame.event.Event(pygame.QUIT)
        sound_handle("MenuMusic", "play", 100, 2,loop= True)


        # Buttons
        self.play_button = ImageButton(
            self.screen,
            True,
            image=alpha_converter(MenuButtons.button_assets["Play"]["img"]),
            position_type="center",
            position=(SCREEN_CENTER[0], SCREEN_CENTER[1] + 2),
        )

        self.cards_button = ImageButton(
            self.screen,
            True,
            image=alpha_converter(MenuButtons.button_assets["Cards"]["img"]),
            position_type="center",
            position=(SCREEN_CENTER[0], SCREEN_CENTER[1] + 102),
        )

        self.credits_button = ImageButton(
            self.screen,
            True,
            image=alpha_converter(
                MenuButtons.button_assets["Credits"]["img"]
            ),
            position_type="center",
            position=(SCREEN_CENTER[0], SCREEN_CENTER[1] + 202),
        )

        self.exit_button = ImageButton(
            self.screen,
            self.quit_event,
            image=alpha_converter(MenuButtons.button_assets["Exit"]["img"]),
            position_type="center",
            position=(SCREEN_CENTER[0], SCREEN_CENTER[1] + 302),
        )

        self.viewlore_button = ImageButton(
            self.screen,
            True,
            image=alpha_converter(
                MenuButtons.button_assets["ViewLore"]["img"]
            ),
            position_type="topleft",
            position=(91, 683),
        )

        self.starttutorial_button = ImageButton(
            self.screen,
            True,
            image=alpha_converter(
                MenuButtons.button_assets["StartTutorial"]["img"]
            ),
            position_type="topleft",
            position=(1065, 685),
        )

    def main_menu(self):

        self.screen.blit(self.bg_main_menu_image, self.bg_main_menu_rect)
        self.play_button.render()
        self.cards_button.render()
        self.credits_button.render()
        self.exit_button.render()
        self.viewlore_button.render()
        self.starttutorial_button.render()

        if self.credits_button.answer():
            self.change_state("CreditsMenu")
        elif self.play_button.answer():
            self.change_state("PlayMenu")
        elif self.cards_button.answer():
            self.change_state("CardsMenu")
        elif self.starttutorial_button.answer():
            self.change_state("TutorialMenu")
            sound_handle("TutorialSpeech1", channel=7)
        elif self.viewlore_button.answer():
            self.change_state("LoreMenu")
            sound_handle("LoreSpeech1", channel=7)
        self.exit_button.answer()

    def state_manager_hook(self, app):
        if len(State.state_tree) >= 2:
            if State.state_tree[1] == self.local_options[1]:
                app.menu_instances["play_menu"].state_manager(app)
            elif State.state_tree[1] == self.local_options[2]:
                app.menu_instances["cards_menu"].state_manager(app)
            elif State.state_tree[1] == self.local_options[3]:
                app.menu_instances["credits_menu"].state_manager(app)
            elif State.state_tree[1] == self.local_options[4]:
                app.menu_instances["tutorial_menu"].state_manager(app)
            elif State.state_tree[1] == self.local_options[5]:
                app.menu_instances["lore_menu"].state_manager(app)
        elif State.state_tree[0] == self.local_options[0]:
            self.main_menu()

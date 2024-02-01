import pygame
from UserInterface.ui_settings import SCREEN_CENTER
from UserInterface.OcgVision.vision_main import State, ImageButton
from UserInterface.MenuTemplates.play_menu_ui import PlayMenu
from UserInterface.MenuTemplates.credits_menu_ui import CreditsMenu
from UserInterface.MenuTemplates.cards_menu_ui import CardsMenu
from Assets.menu_assets import MenuBackgrounds, MenuButtons, alpha_converter
import os


class MainMenu(State):
    def __init__(self, screen):
        super().__init__(
            screen, True, ["MainMenu", "PlayMenu", "CardsMenu", "CreditsMenu"]
        )

        self.bg_main_menu_image = MenuBackgrounds.bg_main_menu_image.convert_alpha()
        self.bg_main_menu_rect = self.bg_main_menu_image.get_rect(
            topleft=(0, 0))

        self.quit_event = pygame.event.Event(pygame.QUIT)

        # Buttons
        self.play_button = ImageButton(
            self.screen,
            True,
            image=alpha_converter(MenuButtons.play_button_image),
            position_type="center",
            position=(SCREEN_CENTER[0], SCREEN_CENTER[1] + 2),
        )

        self.cards_button = ImageButton(
            self.screen,
            True,
            image=alpha_converter(MenuButtons.cards_button_image),
            position_type="center",
            position=(SCREEN_CENTER[0], SCREEN_CENTER[1] + 102),
        )

        self.credits_button = ImageButton(
            self.screen,
            True,
            image=alpha_converter(MenuButtons.credits_button_image),
            position_type="center",
            position=(SCREEN_CENTER[0], SCREEN_CENTER[1] + 202),
        )

        self.exit_button = ImageButton(
            self.screen,
            self.quit_event,
            image=alpha_converter(MenuButtons.exit_button_image),
            position_type="center",
            position=(SCREEN_CENTER[0], SCREEN_CENTER[1] + 302),
        )

        # Options
        self.play_menu = PlayMenu(self.screen)
        self.cards_menu = CardsMenu(self.screen)
        self.credits_menu = CreditsMenu(self.screen)

    def main_menu(self):
        self.screen.blit(self.bg_main_menu_image, self.bg_main_menu_rect)
        self.play_button.render()
        self.cards_button.render()
        self.credits_button.render()
        self.exit_button.render()

        if self.credits_button.answer():
            self.change_state("CreditsMenu")
        elif self.play_button.answer():
            self.change_state("PlayMenu")

        elif self.cards_button.answer():
            self.change_state("CardsMenu")
        self.exit_button.answer()

    def state_manager_hook(self):
        if len(State.state_tree) >= 2:
            if State.state_tree[1] == self.local_options[1]:
                self.play_menu.state_manager()
            elif State.state_tree[1] == self.local_options[2]:
                self.cards_menu.state_manager()
            elif State.state_tree[1] == self.local_options[3]:
                self.credits_menu.state_manager()
        elif State.state_tree[0] == self.local_options[0]:
            self.main_menu()

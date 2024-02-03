import utility
import sys
import pygame
import os
from UserInterface.ui_settings import SCREEN_WIDTH, SCREEN_HEIGHT
from UserInterface.MenuStates.play_menu_ui import PlayMenu
from UserInterface.MenuStates.main_menu_ui import MainMenu
from UserInterface.MenuStates.main_menu_ui import MainMenu
from UserInterface.MenuStates.lore_menu_ui import LoreMenu
from UserInterface.MenuStates.join_menu_ui import JoinMenu
from UserInterface.MenuStates.host_menu_ui import HostMenu
from UserInterface.MenuStates.game_menu_ui import GameMenu
from UserInterface.MenuStates.tutorial_menu_ui import TutorialMenu
from UserInterface.MenuStates.credits_menu_ui import CreditsMenu
from UserInterface.MenuStates.cards_menu_ui import CardsMenu
from SfxEngine.SoundEngine import sound_handle


class OcgGame:
    def __init__(self):
        """
        This class represents the application for the "OCG" game.
        Initializes the App class with a pygame screen, clock, and the MainMenu.

        Attributes
        ---------
            screen: pygame Surface object representing the game window.
            clock: pygame Clock object to control the game's frame rate.
            MainMenu: MainMenu object representing the main menu of the game.

        """
        pygame.init()
        self.logo = pygame.image.load(os.path.join(utility.cwd_path,
                                                   "Assets", "Graphics", "Icons", "app_icon.png",))
        pygame.display.set_icon(self.logo)
        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.display.set_caption("OCG")
        self.clock = pygame.time.Clock()

        # Initialize the menu instances dictionary
        self.menu_instances = {
            'main_menu': MainMenu(self.screen),
            'play_menu': PlayMenu(self.screen),
            'credits_menu': CreditsMenu(self.screen),
            'cards_menu': CardsMenu(self.screen),
            'lore_menu': LoreMenu(self.screen),
            'tutorial_menu': TutorialMenu(self.screen),
            'host_menu': HostMenu(self.screen),
            'join_menu': JoinMenu(self.screen),
            'game_menu': GameMenu(self.screen)
        }

    def start(self):
        """
        Starts the game loop which continues running until the quit event is caught.
        """
        self.running = True
        # sound_handle("ambientmenumusictest2", "ambient_play", 30)
        while self.running:

            self.menu_instances["main_menu"].state_manager(self)
            if pygame.event.get(eventtype=pygame.QUIT):
                self.stop()
            pygame.event.get()

            pygame.display.update()
            self.clock.tick(60)

            # Event Handling

    def stop(self):
        """
        Stops the game loop by quitting pygame and exiting the system.
        """
        self.running = False
        pygame.quit()
        sys.exit()

from operator import is_
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
from UserInterface.MenuStates.lobby_menu_ui import LobbyMenu
from UserInterface.MenuStates.game_menu_ui import GameMenu
from UserInterface.MenuStates.tutorial_menu_ui import TutorialMenu
from UserInterface.MenuStates.credits_menu_ui import CreditsMenu
from UserInterface.MenuStates.cards_menu_ui import CardsMenu
from SfxEngine.SoundEngine import sound_handle
from utility import toggle_mute, get_setting, get_settings, write_settings


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
            'lobby_menu': LobbyMenu(self.screen),
            'game_menu': GameMenu(self.screen)
        }

    def start(self):
        """
        Starts the game loop which continues running until the quit event is caught.
        """

        self.running = True
        while self.running:

            self.menu_instances["main_menu"].state_manager(self)

            if pygame.event.get(eventtype=pygame.QUIT):
                self.stop()
            for event in pygame.event.get():
                if event.type == pygame.KEYUP and event.key == pygame.K_p:
                    print("----------- P KEY PRESSED ------------")
                    print(f"before it was {get_setting('mute', False)}")
                    toggle_mute()
                    print(f"now its {get_setting('mute', False)}")
                    sound_handle(action_type = "mute/unmute", channel = 2)



            pygame.display.update()
            self.clock.tick(60)

            # Event Handling

    def stop(self):
        """
        Stops the game loop by quitting pygame and exiting the system.
        This also writes settings to `./opitions.txt` (save volume/mute changes).
        """
        write_settings(get_settings())
        self.running = False
        pygame.quit()
        sys.exit()

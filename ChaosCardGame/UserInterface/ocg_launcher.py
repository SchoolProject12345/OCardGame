import sys
import pygame
import os
import utility
from UserInterface.ui_settings import SCREEN_WIDTH, SCREEN_HEIGHT
from UserInterface.MenuStates.main_menu_ui import MainMenu
from SfxEngine.SoundEngine import sound_handle


class OcgGame:
    """
    This class represents the application for the "OCG" game.


    Attributes
    ---------
        screen: pygame Surface object representing the game window.
        clock: pygame Clock object to control the game's frame rate.
        MainMenu: MainMenu object representing the main menu of the game.
    """

    def __init__(self):
        """
        Initializes the App class with a pygame screen, clock, and the MainMenu.
        """
        pygame.init()
        self.logo = pygame.image.load(os.path.join(utility.cwd_path,
                                                   "Assets", "Graphics", "Icons", "app_icon.png",))
        pygame.display.set_icon(self.logo)
        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.display.set_caption("OCG")
        self.clock = pygame.time.Clock()
        self.MainMenu = MainMenu(self.screen)

    def start(self):
        """
        Starts the game loop which continues running until the quit event is caught.
        """
        self.running = True
        sound_handle("ambientmenumusictest2", "ambient_play", 30)
        while self.running:

            self.MainMenu.state_manager()
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

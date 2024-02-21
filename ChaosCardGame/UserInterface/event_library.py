import logging
import pygame
from dataclasses import dataclass


@dataclass
class CustomEvents:
    """
    A class to represent all custom events in the game.
    """
    SLOT_CLICKED = pygame.USEREVENT + 1
    UI_STATE = pygame.USEREVENT + 2
    CLOSE_POPUP = pygame.USEREVENT + 3

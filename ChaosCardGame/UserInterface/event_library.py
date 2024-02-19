import logging
import pygame
from dataclasses import dataclass


def fetch_event(event_name: str, dict: dict = None, raw=False) -> pygame.event.Event:
    event_raw = CustomEvents.custom_events[event_name]
    if raw:
        return event_raw
    elif dict == None:
        return pygame.event.Event(event_raw)
    else:
        return pygame.event.Event(event_raw, dict)


@dataclass
class CustomEvents:
    """
    A class to represent all custom events in the game.
    """

    # Custom Events
    custom_events = {
        "SLOT_CLICKED": pygame.USEREVENT + 1,
        "UI_STATE": pygame.USEREVENT + 2,
    }

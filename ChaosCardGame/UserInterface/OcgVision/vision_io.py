import pygame


class KeyRel:
    def __init__(self, key: pygame.key):
        self.key = key

    def update(self, keyup_evt: pygame.KEYUP):
        for event in keyup_evt:
            if event.type != pygame.KEYUP:
                raise ValueError(f"Wrong event.type: {event}")
            if event.key == self.key:
                return True
        return False

## Berda's Soung engine v0.1
from pygame import mixer, mixer_music
import pygame
from pygame.locals import *


import os

pygame.init()

devmode = True
class ButtonSounds():
    # default menu button press
    def ClickSFX12():
        Click12_path = os.path.join(os.getcwd(), "ChaosCardGame", 'SfxEngine', 'SFX', 'ClickSound1-2.wav')
        sfx = pygame.mixer.Sound(Click12_path)
        sfx.play()

    def ClickSFX21():
        Click12_path = os.path.join(os.getcwd(), "ChaosCardGame", 'SfxEngine', 'SFX', 'ClickSound1-2.wav')
        sfx = pygame.mixer.Sound(Click12_path)
        sfx.play()




if devmode:
    sound_played = False

    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.mixer.init()
#    sound = pygame.mixer.Sound("speech.mp3")
    button_color = (255, 0, 0) # Red color
    button_width = 100
    button_height = 50
    button_x = (WINDOW_WIDTH - button_width) // 2
    button_y = (WINDOW_HEIGHT - button_height) // 2
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if button_rect.collidepoint(mouse_pos):
                    ButtonSounds.ClickSFX12()
            elif event.type == MOUSEBUTTONUP:
                mouse_pos = pygame.mouse.get_pos()
                if button_rect.collidepoint(mouse_pos):
                    ButtonSounds.ClickSFX21()

        window.fill((0, 0, 0)) # Fill the window with black color
        pygame.draw.rect(window, button_color, button_rect) # Draw the button
        pygame.display.flip() # Update the display

pygame.quit()
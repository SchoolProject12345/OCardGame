## Berda's Soung engine v0.1
from pygame import mixer, mixer_music
import pygame
from pygame.locals import *

import os

pygame.init()

devmode = True

sound_file_path = os.path.join(os.getcwd(), 'sfxengine', 'SFX', 'ClickSound12.wav')


if devmode:
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.mixer.init()
    sound = pygame.mixer.Sound(sound_file_path)
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
                    sound.play()

        window.fill((0, 0, 0)) # Fill the window with black color
        pygame.draw.rect(window, button_color, button_rect) # Draw the button
        pygame.display.flip() # Update the display

pygame.quit()